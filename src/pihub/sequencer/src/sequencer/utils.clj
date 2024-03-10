(ns sequencer.utils
  (:require
   [expound.alpha :as expound]
   [clojure.spec.alpha :as s]
   [clojure.tools.logging :as log])
  (:import
   [java.io File]
   [java.time.format DateTimeFormatter]
   [java.time LocalDateTime]))

(defn env-variable [v]
  (System/getenv v))

(defn append-to-file
  "Uses spit to append to a file specified with its name as a string, or
   anything else that writer can take as an argument.  s is the string to
   append."
  [file-name s]
  (spit file-name (str s "\n") :append true))


(defn delete-txt-files [dir-path]
  (let [dir (File. dir-path)
        files (.listFiles dir (reify java.io.FilenameFilter
                                (accept [this d f]
                                  (.endsWith f ".txt"))))]
    (doseq [file files]
      (.delete file))))

(defn now-formatted []
  (let [formatter (DateTimeFormatter/ofPattern "dd/MM/yy, HH:mm:ss")
        now (LocalDateTime/now)]
    (.format now formatter)))

(def log-file (env-variable "PIHUB_LOG_FILE"))

(def mix-log-file "log/all_logs.txt")

(defn make-logger
  ([type file]
   (make-logger type file true))
  ([type file add-to-mix?]
   #(let [txt  (str \[ (now-formatted) \]
                    " "
                    \[ type \]
                    ": "
                    %)]
      (append-to-file file txt)
      (when add-to-mix?
        (println txt)
        (append-to-file mix-log-file txt)))))

(def info! (make-logger "INFO" "log/info.txt"))
(def warn! (make-logger "WARN" "log/warnings.txt"))
(def error! (make-logger "ERROR" "log/errors.txt"))
(def log-fact! (make-logger "FACT" "log/facts.txt" false))
;; FIXME change these to false
(def debug! (make-logger "DEBUG" "log/debug.txt" true))

(defn clear-logs! []
  (delete-txt-files "./log"))

(defn session->rule-names [session]
  (-> session :rule-name->node-id))

(defn log-info [s]
  (println (str ">> INFO: " s)))

(defn log-app [s]
  (println (str ">> APP: " s)))

;;;;;;;;;;;;;;;;;;;;;
;;;; UTILS
(defn parse-spec [spec content]
  (let [res (s/conform spec content)]
    (if (= ::s/invalid res)
      (throw (ex-info (expound/expound-str spec content) {}))
      res)))

;; UTILS
(defn now []
  (/ (System/currentTimeMillis) 1000))

;; (defonce *id-counter (atom 1000))

;; (defn new-id []
;;   (let [v @*id-counter]
;;     (swap! *id-counter inc)
;;     v))

(defn flatten-with-separator [vectors]
  (mapcat (fn [v] (concat v [""]))
          vectors))

(comment
  (flatten-with-separator [["rotate" 1] ["wait" 15]])
  ;;
  )
