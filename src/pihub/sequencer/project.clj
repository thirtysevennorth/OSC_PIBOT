(defproject sequencer "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0"
            :url "https://www.eclipse.org/legal/epl-2.0/"}
  :dependencies [[org.clojure/clojure "1.11.1"]
                 ;; NOTE @prod remove these two and uncomment above
                 ;; to completely remove flowstorm debugging
                 ;; [com.github.flow-storm/clojure "RELEASE"]
                 ;; [com.github.flow-storm/flow-storm-dbg "RELEASE"]
                 [org.clojure/core.async "1.6.681"]
                 ;; [org.clojure/core.specs.alpha "0.2.62"]
                 ;; Spec stuff
                 [org.clojure/core.specs.alpha "0.2.62"]
                 [expound "0.9.0"]
                 ;; Rules
                 [net.sekao/odoyle-rules "1.1.0"]
                 ;; OSC
                 [overtone/osc-clj "0.9.0"]
                 ;; Misc utils
                 [nrepl "1.1.0-alpha1"]
                 [org.clojure/tools.logging "1.2.4"]
                 [org.clojure/core.match "1.0.1"]]
  ;; NOTE @prod remove these two as well
  :exclusions [org.clojure/clojure]
  ;; :jvm-opts ["-Dclojure.storm.instrumentEnable=true"
  ;;            "-Dclojure.storm.instrumentOnlyPrefixes=sequencer."]
  :main ^:skip-aot sequencer.core
  ;; :main sequencer.core
  :target-path "target/%s"
  :profiles {:uberjar {:aot :all
                       :jvm-opts ["-Dclojure.compiler.direct-linking=true"]}})
