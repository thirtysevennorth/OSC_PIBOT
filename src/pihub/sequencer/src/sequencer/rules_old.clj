(ns sequencer.rules-old)

;; (rule ::command
;;       '[:when id {:command/scene scene
;;                   :command/time time
;;                   :pibot/id robot-id
;;                   :command/name command
;;                   :command/args args
;;                   ;;
;;                   }
;;         :then-finally
;;         (let [commands (o/query-all session ::command)]
;;           (insert! ::commands ::by-id (assoc)))])

;; (rule ::command-group
;;       '[:when id {:command-group/time time
;;                   :command-group/scene scene
;;                   :command-group/commands commands
;;                   :command-group/bot-id id}])

;; (rule ::command-groups
;;       '[:when
;;         id {:command/scene scene

;;             :command}])

;; (rule ::detect-scenes
;;       '[:when
;;         anything {:command/scene scene}
;;         :app/session {:session/scenes (session-scenes {:then false})}
;;         :then
;;         (insert! :app/session :session/scenes (conj session-scenes scene))])

;; (rule ::group-commands
;;       '[:when
;;         command-id {:command/scene scene
;;                     :command/time time}])

;; (rule ::send-ready-commands
;;       '[:when])

;; (rule ::group-commands-according-to-time
;;       '[:when
;;         command-id {:command/scene scene
;;                     :command/time time}])

#_(rule ::handle-should-dock
        '[:when
          bot-id {:type :pibot
                  ::num n
                  ::should-dock? true
                  ::busy-with-action? (busy? {:then false})}
          :then
          (do
            (when busy?
              (wait-for-goal-confirmation (pibots n)))
            (osc/send! (pibots n) "/action/dock" nil))])

#_(rule ::update-isadora-with-bot-coords
        '[:when
          bot-id {:type :pibot
                  ::num n
                  ::x x
                  ::y y}
          :then
          (osc/send! isadora
                     (format "/pibots/%i/coords" n)
                     x y)])

#_(rule ::update-bot-LEDs
        '[when
          bot-id {:type :pibot
                  ::num n
                  ::set-led cmd}
          :then
          (osc/send! (pibots n) "/set-LED" cmd)])

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#_(rule ::warn-when-bots-near-nogo-zone
        '[:when bot-id {:type :pibot
                        ::name name
                        ::x x
                        ::y y}
          :if (< (distance-to-nearest-nogo x y)
                 min-acceptable-distance-to-nogo-border)
          :then
          (log-warn (format "Bot %s (id: %s) is too close to no-go zone"
                            bot-name
                            bot-id))])

#_(rule ::dock-when-low-battery
        '[:when bot-id {:type :pibot
                        ::name name
                        ::battery-level (battery | (< battery
                                                      min-battery-allowed))}
          :then
          (insert! bot-id ::should-dock? true)])

#_(rule ::send-final-commands
        '[:when {:type ::command
                 ::robot-id robot
                 ::final? true
                 ::final-cmd-str command}
          :then
          (osc/send! robot (str "/ros/execute-cli/" command))])

#_(rule ::handle-should-dock
        '[:when {:type ::robot
                 :id id
                 ::should-dock true}
          :then
          (println (str "Robot " id " needs to dock!"))])

#_(rule ::dock-when-low-battery
        '[:when {:type ::robot
                 :id id
                 ::battery-level (bat | (< bat low-battery-threshold))}
          :then
          (insert id ::should-dock true)])

#_(rule ::time-since-start
        '[:when
          {:id ::time
           ::starting start
           ::current current}
          :then
          (insert ::time ::since-start (- current start))])

;;;;;;;;;;
;;;;;;;;;;

;; (rule ::beep-when-time
;;       '[:when
;;         :app/session {:scene/current-time current-time}
;;         any {:}])

;; (rule ::command-group
;;       '[:when
;;         group-id
;;         {:command-group/time (command-group-time | (<= command-group-time scene-current-time))
;;          :command-group/scene scene
;;          :command-group/commands commands
;;          :command-group/bot-id id
;;          ;;
;;          }])
;; (rule ::reset-fired-with-scene
;;       '[:when
;;         :app/session {:scene/current any}
;;         group-id {:command-group/fired? (true {:then false})}
;;         :then
;;         (insert! group-id :command-group/fired? false)])

#_(rule ::print-command-groups
        '[:when
          command-group-id
          {:command-group/time group-time
           :command-group/scene scene
           :command-group/commands commands
           :command-group/bot-id id
         ;;
           }
          :then
          (debug! (str "COMMAND-GROUP:\n" match))])

#_(rule ::broadcast-startup
        '[:when
          :app/session {:app/start (true {:then not=})}
          id {:osc/client (client {:then false})}
          :then
          (do
            (println "Breadcasting startup!")
            (osc/send! client "/pihub/update/online" 1)
            #_(insert! :app/session :session/has-broadcast-init? true))])

;; (rule ::log-every-fact
;;       '[:when
;;         id {attr v}
;;         :session/time {:time/current (t {:then false})}

;;         :then
;;         #_(when-not (and (= id :session/time)
;;                          (= attr :time/current)))
;;         (log-fact! (str [id attr v t]))])

#_(rule ::warn-when-bots-near-nogo-zone
        '[:when bot-id {:type :pibot
                        ::name name
                        ::x x
                        ::y y}
          :if (< (distance-to-nearest-nogo x y)
                 min-acceptable-distance-to-nogo-border)
          :then
          (log-warn (format "Bot %s (id: %i) is too close to no-go zone"
                            bot-name
                            bot-id))])

;; If we haven't heard from the bot in over a minute
(def alive-update-warning-threshold (* 60 1))

#_(rule ::warn-when-too-long-since-last-alive-update
        '[:when
          :session/time {:time/current t}
          bot-id {:pibot/name name
                  :pibot/last-seen (last-seen {:then false})}
          :then
          (if (> (- t last-seen) alive-update-warning-threshold)
            (warn! (str "Haven't heard from bot " name " for a while, assuming dead.")))])

#_(rule ::dock-when-low-battery
        '[:when bot-id {:pibot/name name
                        :pibot/battery battery
                        :pibot/status :undocked
                        #_(battery | (< battery min-battery))}
          :then
          (if (< battery min-battery)
            (println "low-battery")
            (println "ok battery"))
          #_(do
              (info (format "Bot %s has low battery (%i), it should dock."
                            name
                            battery))
              (insert! bot-id ::should-dock? true))])
