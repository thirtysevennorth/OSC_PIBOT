(ns sequencer.space)

(flatten [[1 2] [3 4]])

(defn lies-inside? [point shape]
  (let [[px py] point
        flat-points (-> shape :points flatten)]
    (case (:type shape)
      :rect
      (let [[x1 y1 x2 y2] flat-points]
        (and (<= (min x1 x2) px (max x1 x2))
             (<= (min y1 y2) py (max y1 y2))))
      :triangle
      (let  [[x1 y1 x2 y2 x3 y3] flat-points
             sign (fn [x1 y1 x2 y2 x3 y3]
                    (- (* (- x1 x3) (- y2 y3))
                       (* (- x2 x3) (- y1 y3))))
             d1 (sign px py x1 y1 x2 y2)
             d2 (sign px py x2 y2 x3 y3)
             d3 (sign px py x3 y3 x1 y1)
             has-neg (or (< d1 0) (< d2 0) (< d3 0))
             has-pos (or (> d1 0) (> d2 0) (> d3 0))
             inside? (not (and has-neg has-pos))]
        inside?)
      "UNKNOWN SHAPE")))

;; TODO flesh out
(def go-zones [{:type :rect
                :points [[0 0] [2 7]]}
               {:type :rect
                :points [[3 4] [5 6]]}
               {:type :triangle
                :pointns [[7 2] [7 5] [9 3]]}])

;; TODO probably not needed at all
(def no-go-zones [{:type :rect
                   :points [[0 0] [2 7]]}
                  {:type :rect
                   :points [[3 4] [5 6]]}
                  {:type :triangle
                   :pointns [[7 2] [7 5] [9 3]]}])

(comment

  (defn dot [v1 v2]
    (reduce + (map * v1 v2)))

  (defn subtract [v1 v2]
    (map - v1 v2))

  (defn length [v]
    (Math/sqrt (dot v v)))

  (defn point-to-line-distance [point line-start line-end]
    (let [v1 (subtract point line-start)
          v2 (subtract line-end line-start)
          len2 (dot v2 v2)
          t (if (> len2 0) (/ (dot v1 v2) len2) 0)
          t (if (< t 0) 0 (if (> t 1)
                            1
                            t))]
      (length (subtract v1 (map * t v2)))))

  (defn point-in-triangle [point triangle]
    (let [v0 (nth triangle 0)
          v1 (nth triangle 1)
          v2 (nth triangle 2)
          d0 (point-to-line-distance point v0 v1)
          d1 (point-to-line-distance point v1 v2)
          d2 (point-to-line-distance point v2 v0)]
      (if (or (<= d0 0) (<= d1 0) (<= d2 0))
        0
        (if (and (>= d0 0) (>= d1 0) (>= d2 0))
          (let [area (* 0.5 (Math/abs (- (* (- (v1 0) (v0 0)) (- (v2 1) (v0 1)))
                                         (* (- (v2 0) (v0 0)) (- (v1 1) (v0 1))))))]
            (if (< (dot (subtract point v0) (map - v1 v0)) 0)
              (- 0.5 d2)
              (if (< (dot (subtract point v1) (map - v2 v1)) 0)
                (- 0.5 d0)
                (if (< (dot (subtract point v2) (map - v0 v2)) 0)
                  (- 0.5 d1)
                  (/ area (Math/max d0 (Math/max d1 d2)))))))
          0))))

  (defn signed-distance-to-triangle [point triangle]
    (let [dist (point-in-triangle point triangle)]
      (- dist (if (<= dist 0) 0 (Math/min (point-to-line-distance point (nth triangle 0) (nth triangle 1))
                                          (Math/min (point-to-line-distance point (nth triangle 1) (nth triangle 2))
                                                    (point-to-line-distance point (nth triangle 2) (nth triangle 0))))))))

;; Example usage:
  (def point [1.0 1.0])
  (def triangle [[0.0 0.0] [2.0 0.0] [1.0 2.0]])
  (println (signed-distance-to-triangle point triangle))

  ;;
  )
