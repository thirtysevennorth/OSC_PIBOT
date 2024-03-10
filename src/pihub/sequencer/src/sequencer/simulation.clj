(ns sequencer.simulation
  (:require [clojure.core.async :as a
             :refer [go-loop timeout <!! >!! <! >!]]))

(defonce *stop (atom false))

(defn do-every-second []
  (go-loop []
    (println "Action performed")
    (<! (timeout 1000))
    (recur))) ; Recur to repeat the action

;; Start the loop
(do-every-second)
