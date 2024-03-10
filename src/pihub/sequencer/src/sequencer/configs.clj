(ns sequencer.configs
  (:require
   [sequencer.osc :as osc :refer [send!]]
   [sequencer.dsl :refer [insert-fact-q!]]
   [sequencer.cues :as cues]
   [sequencer.utils :refer :all]
   [overtone.osc :as oosc]))

(declare pibots)

(defonce *pibot-clients (atom {}))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; General parameters
(def max-distance-without-stopping 5)
(def min-distance-before-stopping 2)

(def wander-min-duration 2)
(def wander-max-duration 7)
(def wander-min-rotation 20)
(def wander-max-rotation 180)
(def min-battery-allowed 20)
(def min-acceptable-distance-to-nogo-border 0.1)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Server
;; FIXME
(defonce sequencer-port (Integer/parseInt (env-variable "PIHUB_OSC_PORT")))
;; (defonce sequencer-port 1234)
(defonce sequencer-server (osc/osc-server sequencer-port))
(info! (str "Sequencer server running on port: " sequencer-port))

;;;;;; OSC Messages
;;;; Update streams
;;;;

;; (oosc/osc-listen sequencer-server (fn [msg] (println "Default listener: " msg)) :debug)

(osc/add-handler sequencer-server "/pihub/reload-cues"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (cues/read-cuesheet!)))

(osc/add-handler sequencer-server "/pihub/set-scene"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (let [[scene] args]
                     (debug! (str "Setting scene to: " scene))
                     (reset! cues/*current-scene scene)
                     (reset! cues/*current-scene-start-time (now))
                     (reset! cues/*current-unfired-group-times
                             (-> @cues/*cues
                                 (get scene)
                                 keys
                                 sort))
                     #_(insert-fact-q! :session :scene/current scene)
                     #_(doseq [fact @cues/*reset-fired-facts]
                         (println fact)
                         (apply insert-fact-q! fact)))))

#_(osc/add-handler sequencer-server "/pibot/update/alive"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[pibot-id ip port] args]
                       #_(println (format "Pibot ID: %i, battery percentage: %i" pibot-id percentage))
                       (insert-fact-q! (str "pibot-" pibot-id) {:pibot/alive? true
                                                                :pibot/last-seen (now)
                                                                :net/addr ip
                                                                :net/port port}))))
;; Battery
(osc/add-handler sequencer-server "/pibot/update/battery"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (let [[pibot-id percentage] args]
                     #_(println (format "Pibot ID: %i, battery percentage: %i" pibot-id percentage))
                     (insert-fact-q! (str "pibot-" pibot-id) {:pibot/battery  percentage
                                                              :battery/last-update (now)}))))

;; Position
(osc/add-handler sequencer-server "/pibot/update/position"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (let [[pibot-id x y angle] args]
                     (insert-fact-q! (str "pibot-" pibot-id) {:pos/x x
                                                              :pos/y y
                                                              :pos/angle angle
                                                              :pos/last-update (now)}))))
;; Docking
(osc/add-handler sequencer-server "/pibot/update/docking"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (println msg)
                   (let [[pibot-id] args]
                     (insert-fact-q! (str "pibot-" pibot-id) {:pibot/status :docking
                                                              :status/last-update (now)}))))

(osc/add-handler sequencer-server "/pibot/update/docked"
                 (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                   (println msg)
                   (let [[pibot-id success] args]
                     (insert-fact-q! (str "pibot-" pibot-id) {:pibot/status {1 :docked
                                                                             0 :failed-to-dock}
                                                              :status/last-update (now)}))))

#_(osc/add-handler sequencer-server "/pibot/update/undocking"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[pibot-id] args]
                       (insert-fact-q! (str "pibot-" pibot-id) {:pibot/status :undocking
                                                                :status/last-update (now)}))))

#_(osc/add-handler sequencer-server "/pibot/update/undocked"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[pibot-id] args]
                       (insert-fact-q! (str "pibot-" pibot-id) {:pibot/status :undocked
                                                                :status/last-update (now)}))))

;; Go-to-point - when navigation has started
#_(osc/add-handler sequencer-server "/pibot/update/action/go-to-point"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[pibot-id point bool] args]
                       (println (format "Pibot ID: %i going to point %i RESULT: %s" pibot-id point bool)))))

;;;; Commands
#_(osc/add-handler sequencer-server "/pibot/command/set-LED"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (println "MSG: " msg)
                     (let [[pibot-id r g b w] args]
                       (case pibot-id
                         -1 (do
                              (println "Sending LED to all...")
                              (doseq [pibot pibots]
                                (send! pibot "/pibot/command/set-LED" -1 r g b w)))
                         (do
                           (println (str "Sending only to bot: " pibot-id))
                           (send! (pibots (dec pibot-id)) "/pibot/command/set-LED" pibot-id r g b w))))))

(comment
  (do
    (println "----------------------------")
    (send! (pibots 1) "pibot/command/set-LED" 2 1606 772 772 772))
  ;;
  )

#_(osc/add-handler sequencer-server "/pibot/command/set-mode-all"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[new-mode] args]
                       (println (format "Setting all pibots to mode %i" new-mode)))))

#_(osc/add-handler sequencer-server "/pibot/command/set-mode"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (let [[pibot-id new-mode] args]
                       (println (format "Setting Pibot ID: %i to mode %i" pibot-id new-mode)))))

#_(osc/add-handler sequencer-server "/pibot/command/stop-all"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (println "Stopping all pibots...")))

#_(osc/add-handler sequencer-server "/test"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (println "MSG: " msg)))

#_(osc/add-handler sequencer-server "/pibot/play-note"
                   (fn [{:keys [src-host src-port path type-tag args] :as msg}]
                     (println "MSG: " msg)
                     #_(send! (pibots (first args)) "/play-note" (second args))))
