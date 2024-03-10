(ns sequencer.cues
  (:require
   [sequencer.dsl :as dsl]
   [odoyle.rules :as o]
   #_[clojure.spec.alpha :as s]
   #_[flow-storm.api :as fs-api]
   [sequencer.utils :as u]))

#_(comment
    (fs-api/local-connect))

(def default-cuesheet-path "resources/cues.edn")

(defn process-commands [commands]
  (->> commands
       u/flatten-with-separator
       (map #(cond
               (string? %) %
               (symbol? %) (str %)
               (number? %) (cond
                             (float? %) %
                             (double? %) %
                             :else (int %))
               :else %))))

(defonce *command-group-ids (atom []))
(defonce *reset-fired-facts (atom []))

(defonce *playing? (atom true))
(defonce *cues (atom {}))
(defonce *current-scene (atom nil))
(defonce *current-scene-start-time (atom 0))
;; (defonce *current-scene-time (atom 0))
(defonce *current-unfired-group-times (atom []))

(defn process-cuesheet [cuesheet]
  (into {} (map (fn [[k v]]
                  [k (into {} (map (fn [[k2 v2]]
                                     (if (sequential? k2)
                                       [(first k2) v2]
                                       [k2 v2]))
                                   v))])
                cuesheet)))

(defn read-cuesheet!
  ([] (read-cuesheet! default-cuesheet-path))
  ([path]
   (u/info! "Reading cues...")
   (reset! *cues
           (-> path slurp clojure.edn/read-string process-cuesheet))
   (u/info! "Cues read.")))

(read-cuesheet!)

#_(defn cuesheet->command-groups [path]
    (let [m (-> path slurp clojure.edn/read-string)
          _ (reset! *cues m)
          m (seq m)]
      (for [[scene commands] m
            [time commands] commands
            [bot-id commands] commands]
        (let [;
              commands (into [] (process-commands commands))
              command-group-map {:thing/type :command-group
                                 :command-group/scene scene
                                 :command-group/time (if (sequential? time) (first time) time)
                                 :command-group/bot-id bot-id
                                 :command-group/fired? false
                                 :command-group/commands commands}
              entity-id [(:command-group/scene command-group-map)
                         (:command-group/time command-group-map)
                         (:command-group/bot-id command-group-map)]]
          #_(println (str "Command group map: " command-group-map))
          [entity-id command-group-map]))))

(comment
  (cuesheet->command-groups default-cuesheet-path)
  ;;
  )

(defonce *cue-command-groups (atom []))

#_(defn insert-cues
    ([session] (insert-cues session default-cuesheet-path))
    ([session path]
     (let [groups (cuesheet->command-groups path)]
       ;; (println "inserting cues" (map count facts))
       #_(reset! *command-group-ids
                 (map first groups))
       #_(reset! *reset-fired-facts
                 (into []
                       (for [id @*command-group-ids]
                         [id :command-group/fired? false])))
       (reset! *cue-command-groups groups)
       (reduce (fn [session fact]
                 ;; (println session)
                 ;; (println fact)
                 (apply (partial o/insert session)
                        fact))
               session
               groups))))

#_(defn insert-reset-fired [session]
    (reduce (fn [session fact]
              (apply (partial o/insert session)
                     fact))
            session
            @*reset-fired-facts))

;;;;;;;;;;;;;;;;;;;;
;; WASTE
(comment
  (defn cuesheet->all-command-facts
    ([] (cuesheet->all-command-facts default-cuesheet-path))
    ([path]
     (for [[scene-num entries] (-> path slurp clojure.edn/read-string seq)
           [time entry] (seq entries)
           [robot-id commands] (seq entry)
           command commands]
       ;; Final modifications here
       (let [time (if (sequential? time) (first time) time)
             ;; args (if (sequential? command))]
             args (rest command)
             args (if (empty? args) nil args)
             command (first command)
             attrs {:command/scene scene-num
                    :command/time time
                    :pibot/id robot-id
                    :command/name command
                    :command/args args}] attrs))))

  (do
    (defn cuesheet->all-command-groups
      ([] (cuesheet->all-command-groups default-cuesheet-path))
      ([path]
       (let [all-commands (cuesheet->all-command-facts path)
             by-scene (sort-by :command/scene all-commands)
             result    (group-by #(select-keys % [:command/scene :command/time :pibot/id])
                                 all-commands)
             ;; by-scene
             ]
         result)))
    (cuesheet->all-command-groups))

  (group-by #(select-keys % [:command/scene :command/time :pibot/id]))

  (loop [commands (cuesheet->all-command-facts)
         acc {}]
    (recur (rest commands)
           (assoc acc)))

  ;; (seq)
  ;; (for [])
  #_(apply hash-map (map (fn [[scene entries]]
                           [scene (group-by :command/time entries)])
                         (seq (group-by :command/scene
                                        (cuesheet->all-command-facts)))))
  ;; (group-by :command/time)           ;
  )
