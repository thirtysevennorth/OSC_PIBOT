(ns sequencer.dsl
  (:require
   [odoyle.rules :as o]
   [sequencer.utils :as u]
   ;; [clojure.algo.generic.functor :only (fmap)]

   ;; [flow-storm.api :as fs-api]
   [clojure.spec.alpha :as s]))

(defonce *id-counter (atom 1000))

(defn new-id []
  (let [counter @*id-counter]
    (swap! *id-counter inc)
    counter))

;;;;;;;;;;;;;;;;;;;;;
;;;; STATE
(defonce *facts-q (atom []))

(defn insert-fact-q! [& args]
  (swap! *facts-q conj args))

(defonce *rules (atom {}))

(defonce *session
  (atom (o/->session)
        #_(reduce o/add-rule rules)))

(defn reset-everything! []
  (reset! *rules {})
  (reset! *session (o/->session)))

(comment
  @*rules
  @*session
  (reset-everything!)
  ;;
  )

;;;;;;;;;;;;;;;;;;;;;
;;;; STATE MANAGEMENT
;; (defn init-session []
;;   )
;; (defn init-session! []
;;   (reset! *session
;;           (reduce o/add-rule (o/->session) @*rules)))

(defn extract-facts [session]
  (let [facts (o/query-all session)
        ;; NOTE do any filtering required here
        ]
    facts))

(defn insert-facts
  ([path-or-facts]
   (insert-facts (o/->session) path-or-facts))
  ([session path-or-facts]
   (insert-facts session path-or-facts false))
  ([session path-or-facts fire?]
   (let [facts (if (instance? java.lang.String path-or-facts)
                 (clojure.edn/read-string (slurp path-or-facts))
                 path-or-facts)
         session (reduce o/insert session facts)]
     (if fire?
       (o/fire-rules session)
       session))))

(defn insert-rules [session rules]
  (reduce o/add-rule session rules))

(def session-store-file "serialized-session.edn")

(defn new-session-with [rules facts]
  (-> (o/->session)
      (insert-rules rules)
      (insert-facts facts)))

;; (defn new-session []
;;   (new-session-with @*rules @*facts))

(defn save-session-facts! []
  (spit session-store-file
        (extract-facts @*session)))

(defn load-session-facts! []
  (reset! @*session
          (insert-facts session-store-file (o/->session) true)))

;; TODO
(defn save-session! []
  nil)

;; (swap! *session o/insert [::test-fact ::test-attr "hi"])

;; (o/query-all @*session)

;; (defonce *rulemap (atom {}))

;;;;;;;;;;;;;;;;;;;;;
;;;; DSL

;; (s/def :timelines.rules/when-entry map?)
(s/def :timelines.rules/when-entry (s/cat :id any? :map map?)
  #_(s/or
     :without-id map?
     :with-id (s/cat :id
                     #(not (instance? clojure.lang.PersistentHashMap %))
                     :map map?)))
(s/def :timelines.rules/then-entry sequential?)
(s/def :timelines.rules/then-finally-entry sequential?)

(s/def :timelines.rules/when-entry-pred
  (s/and list?
         (s/cat :binding symbol?
                :then-clause (s/? (s/and map?
                                         #(contains? % :then)) #_(s/cat :then-kw #{:then} :pred any?))
                :separator #{'|}
                :preds (s/+ (s/or :fn symbol?
                                  :expr list?
                                  :value any?)))))

(comment
  (s/conform :timelines.rules/when-entry-pred
             '(x | pos?, odd?, (< x 10), 7))
  (s/conform :timelines.rules/when-entry-pred
             '(x :then false | pos?, odd?, (< x 10), 7))

  (s/conform :timelines.rules/when-entry
             '[{:test1 321}])
  ;;
  )

(s/def :timelines.rules/when-header #{:when})
(s/def :timelines.rules/then-header #{:then})
(s/def :timelines.rules/then-finally-header #{:then-finally})

(s/def :timelines.rules/when-block
  (s/cat :header :timelines.rules/when-header
         :entry (s/+ :timelines.rules/when-entry)))

(s/def :timelines.rules/then-block
  (s/cat :header :timelines.rules/then-header
         :entry :timelines.rules/then-entry))

(s/def :timelines.rules/then-finally-block
  (s/cat :header :timelines.rules/then-finally-header
         :entry :timelines.rules/then-finally-entry))

(s/def :timelines.rules/def
  (s/cat :when-block :timelines.rules/when-block
         :then-block (s/? :timelines.rules/then-block)
         :then-finally-block (s/? :timelines.rules/then-finally-block)))

(defn parse-ruledef-args [args]
  (reduce #(update %1 %2 :entry)
          #_(try (catch Exception e
                   (str ">>>>>>>> ERROR: rule " rule-name " Is malformed, ignoring...")))
          (u/parse-spec :timelines.rules/def args)
          [:when-block :then-block :then-finally-block]))

(def _ nil)

(defn turn-special-keywords-into-qualified-ones [m]
  (into {} (for [[k v] m]
             [(case k
                :type :thing/type
                ;; :id :thing/id
                k)
              v])))

(defn sym->preds->when-clauses [m]
  (for [[sym preds] m
        pred preds]
    (case (first pred)
      :fn (list (second pred) sym)
      :expr (second pred))))

(defn handle-then-else [maps]
  (letfn [(has-then-clause? [v]
            (= :then (second v)))]
    (for [m maps]
      (into {} (for [[k v] m]
                 [k (if-not (has-then-clause? v)
                      v
                      (conj (first v)
                            (drop 3 v)))])))))

#_((fn [v] (= :then (second v)))
   '(z :then false | (= z 8))
   #_(x | (> x 0)))

(comment
  (handle-then-else
   '[{:key1 (x | (> x 0))
      :key2 "hi"}
     {:key3 (z :then false | (= z 8))}
     {:key3 (z :then false)}])
  ;;
  )

(def rules-to-debug (set (mapv #(keyword "sequencer.rules" (name %))
                               [:update-current-scene-start-time
                                :update-current-scene-current-time
                                :reset-command-groups
                                :run-scene])))

(defn debug-rule [rule]
  (let [println (fn [& args]
                  (u/append-to-file "log/debug-rule.txt"
                                    (with-out-str
                                      (apply clojure.core/println args))))]
    (if (rules-to-debug (:name rule))
      (o/wrap-rule rule
                   {:what
                    (fn [f session new-fact old-fact]
                      (println :what (:name rule) new-fact old-fact)
                      (f session new-fact old-fact))
                    :when
                    (fn [f session match]
                      (println :when (:name rule) match)
                      (f session match))
                    :then
                    (fn [f session match]
                      (println :then (:name rule) match)
                      (f session match))
                    :then-finally
                    (fn [f session]
                      (println :then-finally (:name rule))
                      (f session))})
      rule)))

;; TODO @refactor
;; this is ugly but it does the trick for now
(defn rule [rule-name ruledef]
  (let [parsed-args (parse-ruledef-args ruledef)
        ;; a vec of entry maps
        what-maps (:when-block parsed-args)
        ;; add a gensym-generated ID to all maps
        ;; that don't have an explicit one
        what-maps (for [entry what-maps]
                    (let [id (:id entry)]
                      (-> entry
                          :map
                          (assoc :thing/id (if-not (= id '_)
                                             id
                                             (gensym "anonymous_thing_id_"))))))
        ;; Flesh out :type keywords
        what-maps (map turn-special-keywords-into-qualified-ones what-maps)
        ;; map from symbol to vector of (conformed) predicates
        sym->preds (->> what-maps
                        (reduce
                         (fn [acc m]
                           (into []
                                 (concat acc
                                         (reduce
                                          (fn [acc [_ v]]
                                            (if (s/valid? :timelines.rules/when-entry-pred v)
                                              (conj acc v)
                                              acc))
                                          []
                                          m))))
                         [])
                        (reduce
                         (fn [acc entry]
                           (assoc acc (first entry)
                                  (:preds (s/conform :timelines.rules/when-entry-pred entry))))
                         {}))
        ;; Iterate over every map, turn pred pairs to just the symbol
        what-maps
        (letfn [(cleanup-preds [m]
                  (into {} (for [[k v] m]
                             [k (let [conformed (s/conform :timelines.rules/when-entry-pred v)]
                                  (if (= conformed :clojure.spec.alpha/invalid)
                                    v
                                    (if (contains? conformed :then-clause)
                                      (into []
                                            (take 3 v))
                                      (first v))))])))]
          (map cleanup-preds what-maps))
        ;; all symbol bindings
        sym-bindings (->> what-maps
                          (map #(into [] %))
                          flatten
                          (into #{})
                          (filter symbol?)
                          (into []))
        fn-destructured-args `[~'session {:keys ~sym-bindings :as ~'match}]
        when (sym->preds->when-clauses sym->preds)
        when `(fn ~fn-destructured-args
                (and ~@when))
        symbols (->> what-maps
                     (map vec)
                     flatten
                     (filter symbol?))
        what (into [] (filter #(not= :thing/id (second %))
                              (into [] (for [entry what-maps
                                             [k v] entry]
                                         (if (and (sequential? v)
                                                  (map? (second v))
                                                  (contains? (second v) :then))
                                           [(:thing/id entry) k (first v) (second v)]
                                           [(:thing/id entry) k v])))))
        ;; _  (clojure.pprint/pprint what)
        then `(fn ~fn-destructured-args
                ~(:then-block parsed-args))
        then-finally `(fn [~'session]
                        ~(:then-finally-block parsed-args))
        ;; FIXME DEBUGGING
        m {:what what
           :when  when
           :then  then
           :then-finally then-finally}
        ;; Eval stuff that need to be evaled
        m (reduce (fn [m k] (update m k eval))
                  m
                  [:when :then :then-finally])
        rule (->  (o/->rule rule-name m)
                  debug-rule)
        new-rule? (not (contains? (u/session->rule-names @*session)
                                  rule-name))]
    (swap! *rules assoc rule-name rule)
    #_(if new-rule?
        ;; Simply add to session - doesn't overwrite anything
        (swap! *session o/add-rule rule)
        ;; Serialize session facts, make new session, add rules, add facts back
        (let [facts (extract-facts @*session)]
          (reset! *session (new-session-with @*rules facts))))))

(def insert o/insert)
(def insert! o/insert!)

(defn insert-fact!
  ([e a v]
   (swap! *session #(-> % (o/insert e a v) #_o/fire-rules)))
  ([e map]
   (swap! *session #(-> % (o/insert e map) #_o/fire-rules))))

(comment
  (do
    (println "~~~~~~~~~~~~~")
    (clojure.pprint/pprint
     (rule ::my-rule-name
           '[:when
             block-id {:type ::block
                       ::x (x {:then false} | pos?, odd?, (< x 50))
                       ::test block-y
                       ::z (10 {:then false})}

             _ {:type ::potato
                ::starchiness starch}
             :then
             (println x)
             :then-finally
             (println "finally done!")])))
  ;;
  )
  ;;

(defn fire-rules! []
  (swap! *session #(o/fire-rules %)))

(comment
  (defn modify-maps [data]
    (clojure.walk/postwalk
     (fn [item]
       (if (and (map? item)

                (:then (second item))
                (= (last item) false))
         (assoc item :modified true)
         item))
     data))

  (def sample-data
    '[{:key1 (x | (> x 0))
       :key2 "hi"}
      {:key3 (z {:then false} | (= z 8))}
      {:key3 (z :then false)}])

  (def modified-data (modify-maps sample-data))
  (println modified-data))

(comment

  (into [1 2 3] [4 4 4]))

(u/session->rule-names @*session)

#_(defn set-session-time! [t]
    (swap! *session
           (fn [session]
             (-> session
                 (o/insert [::time ::current t])
                 o/fire-rules))))
