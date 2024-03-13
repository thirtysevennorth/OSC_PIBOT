# Cue List Template and Syntax for PIHUB

The live Cue list is writen in [Clojure](https://clojure.net) and intended to be editable and refreshable on a live basis. The list outlines cues and timings for all robots and devices under control of the pihub, and each scenes actions can be triggered by a single OSC message.

**Pages:**
* [README](https://thirtysevennorth.github.io/OSC_PIBOT/)
* [SOFTWARE EXAMPLES](Examples.md)
* [PI CONFIGURATION](Pi_CONFIGURATION.md)
* [GITHUB REPO](https://github.com/thirtysevennorth/OSC_PIBOT)
* [CUELIST EXAMPLE](CueListExample.md)
* [37 North on GITHUB](https://github.com/thirtysevennorth)


## cue list map structure
The cue list struture is a series of nested maps. The map hierarchy: 1 cue list > 2 scene > 3 time > 4 bot # > 5 specific command.

* scene number (can be labeled either by a number or by a name, e.g. ":intro", ":outro" etc)
	* time in seconds from start of scene
		* bot 1,2,3, etc to command
			* command for bot
			* synchronus command for bot
		* bot 2 
			* command for bot 2
			* synchronus command for bot 2 
	* next time stamp in scene 1

* next scene number
	* time in seconds from start of scene 2
		* bot 1,2,3, etc to command
			* command for bot
			* synchronus command for bot
		* bot 2 
			* command for bot 2
			* synchronus command for bot 2 
	* next time stamp in scene 2

## Example Cue List for two bots
```
;; "description of map"
;; "Scene one, second 0, 	bot 1 SET LED, Bot 2 Set LED"
;; 			  "second 10, 	bot 1 Set-LED, Bot 2 undock, wait, then move 300 cm"
;; 			  "second 20,   bot 1 undock, setLED, wait, mode"
;; 	etc. etc.

{1 {0  {1 [(set-LED 20 0 30 0 30 0 20 0 0 0 0 0 0 0 0 0)]
	    2 [(set-LED 20 0 30 0 100 0 0 0 0 0 0 0 0 0 0 0)]}
    10 {1 [(set-LED 30 0 20 0 100 20 0 30 0 0 0 0 0 0 0 0)]
        2 [(undock)
          (wait 5)
          (move 300 15)]}

    20 {1 [(undock)
    	      (set-LED 15 15 0 0 15 15 0 0 0 0 0 0 0 0 0 0)
    	      (wait 10)
    	      (move 150 10)]
        2 [(rotate 20 15)
           (move 50 10)]
           (wait 5)
           (rotate -20 15)
           (move 50 10)]}

    40 {1 [(rotate 45 6)
    		(wait 5)
    		(rotate 45 8)
    		(wait 5)
    		(rotate 45 11)
    		(wait 5)
    		(rotate 45 15)]	
        2 [(navigate-to 400 100 6)]}
    80 {1 [(set-LED 0 0 10 30 0 0 10 30 0 0 0 0 0 0 0 0)
   			(navigate-to 400 -100 8)]
        2 [(navigate-to 50 0 6)]}
    100 {1 [(rotate 180 6)]
         2 [(dock)
            (set-LED 100 100 10 30 0 0 0 0 0 0 0 0 0 0 0 0)]}
    110 {1 [(navigate-to 50 20 6)
    	    (dock)]
    ;;
    }
 2 {0 {1 [(scene 2 123)
          (hello 3 222)]
       2 [(navigate-to 800 200 5)]}
    [10 40] {2 [(set-LED 255 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0)
                (dock)]}}}
                ```

