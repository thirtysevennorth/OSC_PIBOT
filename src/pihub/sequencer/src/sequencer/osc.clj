(ns sequencer.osc
  (:require [overtone.osc :as osc]
            [clojure.core.match :refer [match]]
            #_[sequencer.configs :refer :all]
            ;;
            ))

(def osc-client osc/osc-client)
(def osc-server osc/osc-server)

;; SERVER
(defn osc-handler [{:keys [src-host src-port path type-tag args] :as msg}]
  (println "MSG: " msg))

(defn add-handler [server path f]
  (osc/osc-handle server path f))

(defn send! [client path & args]
  ;; (println (str "Args from send!: " args))
  (apply (partial osc/osc-send client path) args))

#_(defn close []
    (osc/osc-close sequencer-server)
    (doseq [client clients]
      (osc/osc-close client)))
