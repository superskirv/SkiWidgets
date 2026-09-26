# SkiWidgets

## About:
Drop in replacements for tk.Entry, tk.Text, ttk.Combobox, tk.Scale, and ttk.notebook. Though some functions may not be availible, I know notebook has a few issues I havent tracked down for complete all issues. These were all written mostly by ai, with very little involvement from me. If you see or run into issues, please let me know.

### Usage
Use these special widgets as drop in replacements for the tk widget they are.
- class SkiEntry(tk.Entry)
- class SkiText(tk.Text)
- class SkiCombobox(ttk.Combobox)
- class SkiScale(tk.Scale) # Basically...
- class SkiNotebook(ttk.notebook) # Basically...

## SkiEntry
-This works exactly as you would imagine a tk.Entry would work. The is a glitch, at least on linux when you have text highlighted and paste more text in that it does not delete the highlighted text and appends the pasted text before the highlighted, leaving you with both. This widget corrects that and deletes the highlighted text and then pastes the text in.
-The additional added features built in is a copy/paste right-click menu and the undo/redo [ctrl-z/y] features.

## SkiText
This works exactly as you would imagine a tk.Text would work. The is a glitch, at least on linux when you have text highlighted and paste more text in that it does not delete the highlighted text and appends the pasted text before the highlighted, leaving you with both. This widget corrects that and deletes the highlighted text and then pastes the text in.
The additional added features built in is a copy/paste right-click menu and the undo/redo [ctrl-z/y] features.

## SkiCombobox
This is a drop in replacement for ttk.Combobox, it has similar features corrected as the tk.Entry and tk.Text when typing is enabled.
The additional added features built in is a copy/paste right-click menu and the undo/redo [ctrl-z/y] features. As well as a deselect option because on my system it is difficult to remove the highlight when typing is disabled.

## SkiScale
This is a very unique widget, its actually using a ttk.Frame and then inside a SkiEntry and a tk.Scale. Like all of these widgets it will work as a direct replacement of tk.Scale, however if you use the new flags you will get much more functionality.
- Custom params
  - show_entry: This shows a SkiEntry to the right of the scale, though technically it has a vertical orientation I have not tested that enough.
  - round: Number of decimals places to round the scale number too.
  - digits: Number of digits displayed on SkiEntry. This makes the gui more compact. The system will try to guess based on to and from.
  - break_limit: This allows the SkiEntry to break out of the scales limits, though it still rounds to the resolution size.
  - troughcolor: Background color of slider trough (default: None)
  - sliderrelief: Relief style of slider (default: tk.FLAT)

SkiEntry: Supports all SkiEntry features, copy/paste, and if typing undo/redo
Hotkeys: When focused, arrow keys increment/decrement by `resolution`.
Out of Range Visual Feedback: When `break_limit=True` and value exceeds bounds, entry text turns **red**.

## SkiNotebook
This is an very unique take on ttk.notebook. Though technically imported as a ttk.Frame, it builds a custom notebook that trys to automatically figure out how many tabs can fit in the space given. And adds 'arrow' tabs and a 'config' tab.

The arrow tabs, when clicked move the viewable window of tabs over by 1. Never letting you actually see the arrow tab, it swaps back to the previous viewed tab after moving the tabs. It moves the tabs by hiding and unhiding tabs.

The config tab, when enabled, allows you to see some debug information(if debug is enabled) and change the spacing of the tabs for auto-guessing the tab sizes. As well as allowing you to rename, or lock the tabs.

Tab Locking, you can lock tabs, forcing them to always be visible while you scroll through tabs. This adds a lock emoji to the tab name. You can not lock more tabs than are visible, but if you resize the frame then more tabs than should be visible will be squished into the tab bar untill you unlock them.
- Custom params
  - max_tabs_visible: Maximum visible user tabs visibile on the notebook, default 5.
  - auto_max_tabs: Enable automatic calculation for max tabs, default True.
  - config_tab: Enables the config tab next to the left arrow tab, used to lock/unlock tabs and perform some very minor tab operations, default True
  - debug_mode: Enables some very minor debug information on the config tab, may be useful for building the app, Default False

## TODO:
- SkiEntry, SkiText, SkiCombo: Need to add a "Cut" option to the right-click menu.
- SkiNotebook: I need to expose the locking/unlocking tabs to the user for outside class use.
- SkiNotebook: I need to change the way some functions get the name, so we always return the true name and not with the lock emoji.
- SkiNotebook: I need to make the lock emoji a user set "string" option.
- SkiNotebook: I need to make add more options to configure the color theme for internal widgets.

## More to do:
Im sure there is functionality that I missed in some of these widget replacements. If you have suggestions please let me know. Although I feel like most suggestions will be specific to your project, I am open to hear about it. And even if I dont add your specific use case, I may add the hooks in that you use to allow further customization to the widgets.
