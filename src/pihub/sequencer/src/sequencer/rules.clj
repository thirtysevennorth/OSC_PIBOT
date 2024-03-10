(ns sequencer.rules
  (:require [sequencer.configs :refer :all]
            [sequencer.dsl :refer [*session *rules rule
                                   fire-rules! insert! insert
                                   *facts-q insert-fact-q!] :as dsl]
            [sequencer.dsl :refer [rule insert-fact-q!]]
            [sequencer.utils :refer :all]
            [sequencer.cues :as cues]
            [odoyle.rules :as o]
            [sequencer.osc :as osc]))

(comment
  (def test-client (osc/osc-client "192.168.1.212" 1237))
  (println "hi")
  (osc/send! test-client "/hello" 1 2 3 4)
  ;;
  )

(comment
  (reset! *session (o/->session))
  (clojure.pprint/pprint
   *session)
  (reset! *session (init-session)))

(def min-battery 20)

(def pibot-default-attrs
  {:osc/listening? true
   :pibot/charging? true
   ;; one of [:docked, :undocked, :docking, :undocking]
   :pibot/status :docked})

(defn set-scene! [scene]
  (swap! *session #(o/insert % :app/session :scene/current scene)))

(defn init-facts []
  [#_[:app/session :session/has-broadcast-init? false]
   ;; [:session :app/started? true]
   [:session :session/playing? true]
   [:session :time/starting (now)]
   [:session :time/current (now)]
   [:session :time/last-update (now)]
   ["pibot-1" (into pibot-default-attrs
                    {:pibot/name "pibot-1"
                     :pibot/id 1
                     :net/addr (env-variable "PIBOT_1_OSC_IP") #_(env-variable "MY_IP") ;;
                     :net/port (Integer/parseInt (env-variable "PIBOT_OSC_PORT"))
                     ;; NOTE update this
                     :pibot/base-coords [12, 34]})]
   ["pibot-2" (into pibot-default-attrs
                    {:pibot/name "pibot-2"
                     :pibot/id 2
                     :net/addr (env-variable "PIBOT_2_OSC_IP")
                     :net/port (Integer/parseInt (env-variable "PIBOT_OSC_PORT"))
                     :pibot/base-coords [12, 34]})]
   #_["my-test-client" {:net/addr #_(env-variable "MY_IP") "192.168.1.238"
                      :net/port (Integer/parseInt (env-variable "PIBOT_OSC_PORT"))
                      :pibot/id 3}]
   ["isadora" {:net/addr (env-variable "ISADORA_OSC_IP")
               ;; :osc/listening? false
               :net/port (Integer/parseInt (env-variable "ISADORA_OSC_PORT"))
               :osc/client :test-osc-client}]])

(comment
  (init-facts))

(defn insert-init-facts [session]
  (reduce  (fn [session fact]
             (apply (partial o/insert session) fact))
           session
           (init-facts)))

(defn add-rules [session]
  (reduce o/add-rule session (vals @*rules)))

(defn init-session []
  (-> (o/->session)
      add-rules
      insert-init-facts
      ;; cues/insert-cues
      ))

(defn init-session! []
  (info! "Initializing session.")
  (cues/read-cuesheet!)
  (reset! *session (init-session)))

;; Automatically (re)make osc clients whenever
;; the IP addresses and ports are known/changed
(rule ::make-osc-clients
      '[:when id {:net/addr addr
                  :net/port port
                  :pibot/id bot-id}
        :then
        (do
          (debug! (str "Making osc client with addr: " addr " and port: " port))
          (let [client (osc/osc-client addr port)]
            (insert! id :osc/client client)
            (swap! *pibot-clients #(assoc % bot-id client))
            #_(debug! (str "Pibot clients: " @*pibot-clients))))])

#_(rule ::update-current-scene-start-time
        '[:when
          :session {:time/current (t {:then false})
                    :scene/current scene}
          :then
          (do
            (debug! (str "Scene " scene " started at time " t))
            (insert! :session :scene/start-time t)
            (insert! :session :command-groups/reset? true)
            #_(insert! :session :scene/current-time 0))])

#_(rule ::update-current-scene-current-time
        '[:when
          :session {:time/current t
                    :scene/start-time (start-time {:then false})}
          :then
          (let [current-time (- t start-time)]
          ;; (debug! (str "The current scene time is: " (float current-time)))
            (insert! :session :scene/current-time current-time))])

#_(rule ::reset-command-groups
        '[:when
          :session {:command-groups/reset? true}
          id {:command-group/fired? (true {:then false})}
          :then
          (do
            (debug! (str "Un-firing group with id: " id))
            (insert! id :command-group/fired? false))])

#_(rule ::run-scene
        '[:when
          :session {:session/playing? (true {:then false})
                    :scene/current (scene {:then false})
                    :scene/current-time scene-current-time}

          command-group-id
          {:command-group/time (group-time {:then false}
                                           | (>= scene-current-time group-time))
           :command-group/fired? (false {:then false})
           :command-group/scene (scene {:then false})
           :command-group/commands (commands {:then false})
           :command-group/bot-id (bot-id {:then false})}

          bot {:pibot/id (bot-id {:then false})
               :osc/client (client {:then false})}

          :then
          (let [osc-message-addr "/pibot/command/command-list"
                osc-message (into [] (concat [(int bot-id)] commands))
                osc-send-message-args (into [] (concat [client osc-message-addr]
                                                       osc-message))]
            (debug! (str "RUN-SCENE: "
                         scene " "
                         (float scene-current-time) " "
                         command-group-id " "
                         (float group-time) " "
                         bot-id " "
                         commands))
            (insert! command-group-id :command-group/fired? true)
            #_(debug! (str "RUN-SCENE: " osc-send-message-args))
            #_(apply osc/send! osc-send-message-args))])

(comment
  @*session
  @*rules
  ;; Empty session with rules
  (reset! *session  (reduce o/add-rule (o/->session) @*rules))

  (swap! *session
         (fn [sess]
           (o/insert sess ::test ::val "Hello! hi!")))

  (swap! *session #(o/fire-rules %))

  (o/query-all @*session)

  (def facts (dsl/extract-facts @*session))

  (swap! *session
         (fn [sess]
           (dsl/insert-facts facts sess)))

  (swap! *session o/fire-rules)

  (swap! *session o/insert ::test ::val "Hello test!")

  (insert-fact-q! ::test ::val "Hello test!")
  (reset! *session (o/->session))

  (swap! *session (fn [sess]
                    (reduce o/add-rule (o/->session) rules)))

  (swap! *session o/insert ::test {::val "Hello!"
                                   ::done? false})
  (o/fire-rules @*session)
  @*facts-q
  (println "hi")
  ;;
  )

#_(rule ::print-time
        '[:when :session/time {:time/current t}
          :then
          (println (str "Current time is: " t))])

#_(rule ::print-scene-time
        '[:when :app/session {:scene/current-time t}
          :then
          (println (str "Current Scene time is: " t))])

#_(rule ::update-every-second
        '[:when :session/time {:time/current t
                               :time/last-update
                               (t-last {:then false}
                                       | (> (- t t-last) 5.0))}
          :then
          (do
            (debug! ("Five seconds have passed: " t))
            (insert! :session/time :time/last-update t))])
