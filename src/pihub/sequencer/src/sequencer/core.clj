(ns sequencer.core
  (:require [sequencer.dsl :refer [*session *rules rule insert-fact!
                                   fire-rules! insert! *facts-q insert-fact-q!] :as dsl]
            ;; [flow-storm.api :as fs-api]
            [odoyle.rules :as o]
            [nrepl.server :as nrepl]
            [sequencer.utils :refer :all]
            [sequencer.rules :as rules]
            [sequencer.osc :as osc]
            [sequencer.cues :as cue :refer [*playing? *cues *current-scene
                                            *current-scene-start-time
                                            *current-unfired-group-times]]
            [sequencer.configs :refer [*pibot-clients]]
            #_[sequencer.osc :as osc :refer [pibots isadora]]))

;; (comment
;;   (fs-api/local-connect))

(def *should-quit? (atom false))

(comment
  (reset! *should-quit? true)
  ;;
  )

(def nrepl-server-port 7888)
(def sequencer-port (System/getenv "PIHUB_OSC_PORT"))
(def my-ip (System/getenv "MY_IP"))

(defn start-nrepl-server! [port]
  (info! "Starting nrepl server...")
  (nrepl/start-server :port port)
  (info! (str "... nrepl server started, listening on IP=" my-ip
              " and port=" port)))

(def target-fps 30)
(def target-spf (/ 1 target-fps))
(comment
  (doseq [[bot-id commands] (get-in @*cues [1 3])]
    (println bot-id commands))

  ;;
  )
(defn run-cuesheet! [t]
  (if (and @*playing?
           @*current-scene
           (seq @*current-unfired-group-times))
    (let [scene-current-time (- t @*current-scene-start-time)]
      (while (and
              (seq @*current-unfired-group-times)
              (<= (first @*current-unfired-group-times) scene-current-time))
        (let [event-time (first @*current-unfired-group-times)
              events (get-in @*cues [@*current-scene event-time])]
          (doseq [[bot-id commands] (seq events)]
            (let [commands (cue/process-commands commands)
                  _ (println commands)
                  client (@*pibot-clients bot-id)
                  osc-message-addr "/pibot/command/command-list"
                  osc-message (into [] (concat [(int bot-id)] commands))
                  osc-send-message-args (into [] (concat [client osc-message-addr] osc-message))
                  ;;
                  ]
              ;; TODO error checking (e.g for client missing
              (if client
                (do
                  (println (str "Sending: " osc-send-message-args))
                  (apply osc/send! osc-send-message-args))
                (error! (str "Bot with id=" bot-id " doesn't seem to have an OSC client...")))))
          (swap! *current-unfired-group-times rest))))
    #_(println (str "run-cuesheet!: nothing to do..."))))

(defn start-main-loop []
  (info! "Starting main loop...")
  (loop []
    (let [loop-start-time (now)]
      ;; Quit if it's been requested
      (if @*should-quit?
        (do
          (warn! "Main loop quit requested, quitting...")
          (reset! *should-quit? false))
        (do
          ;; Insert facts from queue and clear it
          (swap! *facts-q
                 (fn [q]
                   (doseq [f q]
                     (apply insert-fact! f))
                   ;; reset queue to empty
                   []))
          ;; Update time and fire rules
          (let [current-time (now)]
            (insert-fact! :session :time/current current-time)
            (fire-rules!)
            (run-cuesheet! current-time))
          ;; Sleep logic
          (let [new-time (now)
                time-it-took (-  new-time loop-start-time)
                time-to-sleep (- target-spf time-it-took)]
            ;; (debug! (str "Main loop took: " time-it-took "s, time to sleep for: " time-to-sleep))
            #_(when (pos? time-to-sleep)
                (Thread/sleep (int (* time-to-sleep 1000))))
            (Thread/sleep 250)
            (recur)))))))

(comment
  ;; start
  (def main-loop-thread (future (-main)))
  ;; Quit
  (reset! *should-quit? true)
  ;; Reset
  (rules/init-session!)

  (clojure.pprint/pprint (group-by first (o/query-all @*session)))

  (insert-fact-q! "pibot-1" :pibot/battery 2)

  (insert-fact-q! :app/session :scene/current 1)
  (o/query-all @*session)
  (swap! *session o/fire-rules)
  @*facts-q
  ;;
  )

(defn -main [& args]
  (start-nrepl-server! nrepl-server-port)
  (clear-logs!)
  (rules/init-session!)
  ;; Loop infinitely
  ;; NOTE blocks
  ;; TODO do this on separate thread?
  (start-main-loop)
  #_(System/exit 0))
