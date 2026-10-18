import tkinter as tk
from tkinter import ttk, font

# Use these special widgets as drop in replacements for the tk widget they are.
# class SkiEntry(tk.Entry)
# class SkiText(tk.Text)
# class SkiCombobox(ttk.Combobox)
# class SkiScale(tk.Scale) #Basically...
# class SkiNotebook(ttk.notebook) #Basically...

class SkiEntry(tk.Entry):
    """Simple Entry widget with undo/redo and auto-closing context menu."""
    
    VERSION = "1.1"
    MENU_TIMEOUT_MS = 3000
    
    def __init__(self, parent, **kwargs):
        defaults = {
            "bg": None,                 # "#3a3a3a",
            "fg": None,                 # "#ffffff",
            "insertbackground": None,   # "white",
            "font": None,               # ("Courier", 10),
            "highlightthickness": None, # 0
        }
        
        for key, value in defaults.items():
            if key not in kwargs:
                if value is not None:
                    kwargs[key] = value
        
        super().__init__(parent, **kwargs)
        
        # Simple undo/redo stacks
        self._undo_stack = []
        self._redo_stack = []
        
        # Menu timeout tracking
        self._menu_timeout_id = None
        
        # --- Context Menu Setup ---
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Select All", command=self._select_all_event)
        self.menu.add_separator()
        self.menu.add_command(label="Copy", command=self._do_copy_event)
        self.menu.add_command(label="Paste", command=self._do_paste_event)
        
        # Bind focus out event to close menu
        self.bind("<FocusOut>", self._on_focus_out)
        # --------------------------

        # Bind keys
        self.bind("<Key>", self._on_key_press)
        self.bind("<Control-z>", self._do_undo)
        self.bind("<Control-y>", self._do_redo)
        self.bind("<Control-v>", self._custom_paste)
        self.bind("<Control-a>", self._select_all)
        
        # Bind Right Click (Windows/Linux) and Ctrl+Click (Mac)
        self.bind("<Button-3>", self.show_menu)
        self.bind("<Control-Button-1>", self.show_menu)
    
    def _save_state(self):
        """Save current text to undo stack, clear redo."""
        current_text = self.get()
        
        if self._undo_stack and self._undo_stack[-1] == current_text:
            return
        
        self._redo_stack.clear()
        self._undo_stack.append(current_text)
        
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
    
    def _on_key_press(self, event):
        """Save state before every keystroke (unless it's undo/redo)."""
        if event.keysym.lower() in ('control_z', 'control_y'):
            return
        self._save_state()
    
    def _do_undo(self, event=None):
        """Undo (Ctrl+Z)."""
        if len(self._undo_stack) <= 1:
            return "break"
        
        self._redo_stack.append(self.get())
        self._undo_stack.pop()
        prev_text = self._undo_stack[-1]
        self.delete(0, tk.END)
        self.insert(0, prev_text)
        
        return "break"
    
    def _do_redo(self, event=None):
        """Redo (Ctrl+Y)."""
        if not self._redo_stack:
            return "break"
        
        self._undo_stack.append(self.get())
        next_text = self._redo_stack.pop()
        self.delete(0, tk.END)
        self.insert(0, next_text)
        
        return "break"
    
    def _custom_paste(self, event):
        """Handle paste - clears redo stack."""
        # FIX: Save current state BEFORE pasting so we can undo it
        self._save_state()
        
        try:
            clipboard_text = self.clipboard_get()
            
            try:
                start = int(self.index("sel.first"))
                end = int(self.index("sel.last"))
                self.delete(start, end)
            except tk.TclError:
                pass
            
            self._redo_stack.clear()
            self.insert(tk.INSERT, clipboard_text)
            self.select_clear()
            
            return "break"
            
        except tk.TclError:
            pass

    # --- Menu Command Wrappers ---
    def _select_all_event(self):
        self._select_all(None)

    def _do_copy_event(self):
        """Copy selected text to clipboard."""
        try:
            start = int(self.index("sel.first"))
            end = int(self.index("sel.last"))
            text_to_copy = self.get()[start:end]  # ✅ Correct approach for Entry
        except tk.TclError:
            text_to_copy = self.get()
            
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        
    def _do_paste_event(self):
        self._custom_paste(None)
    # ----------------------------

    def show_menu(self, event):
        self._close_menu()

        try:
            self.mark_set("insert", "%d.%d" % (event.x, event.y))
            self.icursor(tk.INSERT)
        except Exception:
            pass

        x = event.x_root
        y = event.y_root

        if not hasattr(self.menu, "_focus_out_handler_set"):
            self.menu.bind("<FocusOut>", lambda e: self._close_menu())
            self.menu._focus_out_handler_set = True

        self.menu.post(x, y)
        self.menu.focus_set()

        self._menu_timeout_id = self.after(self.MENU_TIMEOUT_MS, self._close_menu)

    def _close_menu(self):
        """Cancel any pending menu timeout and hide the menu if shown."""
        self._cancel_menu_timeout()
        try:
            self.menu.unpost()
        except tk.TclError:
            pass

    def _cancel_menu_timeout(self):
        """Cancel any pending menu auto-close timeout."""
        if self._menu_timeout_id:
            try:
                self.after_cancel(self._menu_timeout_id)
            except tk.TclError:
                pass
            self._menu_timeout_id = None

    def _on_focus_out(self, event=None):
        """Close menu when widget loses focus."""
        self._close_menu()
    
    def _select_all(self, event):
        """Select all (Ctrl+A)."""
        self.select_range(0, tk.END)
        return "break"

class SkiText(tk.Text):
    """Simple Text widget with undo/redo and auto-closing context menu."""
    
    VERSION = "1.2"
    MENU_TIMEOUT_MS = 3000
    
    def __init__(self, parent, **kwargs):
        defaults = {
            "bg": None,                 # "#3a3a3a",
            "fg": None,                 # "#ffffff",
            "insertbackground": None,   # "white",
            "font": None,               # ("Courier", 10),
            "wrap": None,               # "word",
            "highlightthickness": None, # 0
        }
        
        for key, value in defaults.items():
            if key not in kwargs:
                if value is not None:
                    kwargs[key] = value
        
        super().__init__(parent, **kwargs)
        
        # --- Undo/Redo Setup ---
        self._undo_stack = []
        self._redo_stack = []
        
        # --- Menu Setup ---
        self._menu_timeout_id = None
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Select All", command=self._select_all_event)
        self.menu.add_separator()
        self.menu.add_command(label="Copy", command=self._do_copy_event)
        self.menu.add_command(label="Paste", command=self._do_paste_event)
        
        # --- Event Bindings ---
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Key>", self._on_key_press)
        self.bind("<Control-z>", self._do_undo)
        self.bind("<Control-y>", self._do_redo)
        self.bind("<Control-v>", self._custom_paste)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Button-3>", self.show_menu)
        self.bind("<Control-Button-1>", self.show_menu)
    
    def _save_state(self):
        """Save current text to undo stack, clear redo."""
        current_text = self.get("1.0", "end-1c")
        
        if self._undo_stack and self._undo_stack[-1] == current_text:
            return
        
        self._redo_stack.clear()
        self._undo_stack.append(current_text)
        
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _char_to_index(self, char_pos):
        """Convert character position to Tkinter index (line.col)."""
        if char_pos < 0:
            return None
            
        if char_pos == 0:
            return "1.0"
        
        try:
            text = self.get("1.0", "end-1c")
        except tk.TclError:
            return None
        
        if char_pos > len(text):
            char_pos = len(text)
        
        line_num = 1
        col_num = 0
        
        for i in range(char_pos):
            if text[i] == '\n':
                line_num += 1
                col_num = 0
            else:
                col_num += 1
        
        return f"{line_num}.{col_num}"
    
    # ==========================================================================
    # EVENT HANDLERS
    # ==========================================================================
    
    def _on_key_press(self, event):
        """
        Called on EVERY keystroke.
        Saves state for undo functionality.
        """
        # Skip undo/redo keys from saving state
        if event.keysym.lower() in ('control_z', 'control_y'):
            return "break"
        
        # Save state for undo
        self._save_state()
        
        return ""  # Let the key event continue normally
    
    def _do_undo(self, event=None):
        """Undo (Ctrl+Z)."""
        if len(self._undo_stack) <= 1:
            return "break"
        
        self._redo_stack.append(self.get("1.0", "end-1c"))
        self._undo_stack.pop()
        prev_text = self._undo_stack[-1]
        self.delete("1.0", "end")
        self.insert("1.0", prev_text)
        
        return "break"
    
    def _do_redo(self, event=None):
        """Redo (Ctrl+Y)."""
        if not self._redo_stack:
            return "break"
        
        self._undo_stack.append(self.get("1.0", "end-1c"))
        next_text = self._redo_stack.pop()
        self.delete("1.0", "end")
        self.insert("1.0", next_text)
        
        return "break"
    
    def _custom_paste(self, event):
        """Handle paste - clears redo stack."""
        self._save_state()
        
        try:
            clipboard_text = self.clipboard_get()
            
            try:
                start = self.index("sel.first")
                end = self.index("sel.last")
                self.delete(start, end)
            except tk.TclError:
                pass
            
            self._redo_stack.clear()
            self.insert("insert", clipboard_text)
            self.tag_remove("sel", "1.0", "end")
            
            return "break"
            
        except tk.TclError:
            pass

    # --- Menu Command Wrappers ---
    def _select_all_event(self):
        self._select_all(None)

    def _do_copy_event(self):
        try:
            start = self.index("sel.first")
            end = self.index("sel.last")
            text_to_copy = self.get(start, end)
        except tk.TclError:
            text_to_copy = self.get("1.0", "end-1c")
            
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        
    def _do_paste_event(self):
        self._custom_paste(None)
    # ----------------------------

    def show_menu(self, event):
        self._close_menu()

        x = event.x_root
        y = event.y_root

        if not hasattr(self.menu, "_focus_out_handler_set"):
            self.menu.bind("<FocusOut>", lambda e: self._close_menu())
            self.menu._focus_out_handler_set = True

        self.menu.post(x, y)
        self.menu.focus_set()

        self._menu_timeout_id = self.after(self.MENU_TIMEOUT_MS, self._close_menu)

    def _close_menu(self):
        """Cancel any pending menu timeout and hide the menu if shown."""
        self._cancel_menu_timeout()
        try:
            self.menu.unpost()
        except tk.TclError:
            pass

    def _cancel_menu_timeout(self):
        """Cancel any pending menu auto-close timeout."""
        if self._menu_timeout_id:
            try:
                self.after_cancel(self._menu_timeout_id)
            except tk.TclError:
                pass
            self._menu_timeout_id = None

    def _on_focus_out(self, event=None):
        """Close menu when widget loses focus."""
        self._close_menu()

    def _select_all(self, event):
        self.tag_add("sel", "1.0", "end-1c")
        return "break"

    def destroy(self):
        self._cancel_menu_timeout()
        super().destroy()

class SkiCombobox(ttk.Combobox):
    """
    Drop-in replacement for ttk.Combobox with:
      - Undo/Redo (Ctrl+Z / Ctrl+Y) for typed edits
      - Context menu (Select All/Copy/Paste/Deselect) with auto-close
      - Dark theme styling via ttk.Style
    Naming now aligned with SkiEntry / SkiText.
    """
    VERSION = "1.2"
    MENU_TIMEOUT_MS = 3000

    def __init__(self, parent, values=None, width=20, **kwargs):
        # Apply defaults before calling super().__init__
        defaults = {}
        if values is not None:
            defaults["values"] = list(values)

        for key, value in defaults.items():
            if key not in kwargs:
                if value is not None:
                    kwargs[key] = value

        super().__init__(parent, **kwargs)

        # Undo/redo stacks (same names as SkiEntry/SkiText)
        self._undo_stack = []
        self._redo_stack = []

        # Menu timeout tracking (same name as SkiEntry/SkiText)
        self._menu_timeout_id = None

        # Context menu (now named 'menu' like SkiEntry/SkiText)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Select All", command=self._select_all_event)
        self.menu.add_command(label="Deselect", command=self._deselect_event)
        self.menu.add_separator()
        self.menu.add_command(label="Copy", command=self._do_copy_event)
        self.menu.add_command(label="Paste", command=self._do_paste_event)

        # Bindings
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Key>", self._on_key_press)
        self.bind("<Control-z>", self._do_undo)
        self.bind("<Control-y>", self._do_redo)
        self.bind("<Control-v>", self._custom_paste)
        self.bind("<Control-a>", self._select_all)
        self.bind("<Button-3>", self.show_menu)
        self.bind("<Control-Button-1>", self.show_menu)
        self.bind("<<ComboboxSelected>>", self._on_combobox_selected)

    # ---------- Standard ttk.Combobox API ----------

    def get(self):
        """Return current text value."""
        return str(super().get())

    def set(self, value):
        """Set current text value (same as ttk.Combobox.set)."""
        super().set(str(value))

    def current(self, index=None):
        """Get/set selected index among values (same as ttk.Combobox.current)."""
        return super().current(index)

    def values(self):
        """Return list of dropdown values (alias for 'values' config)."""
        return list(self.cget("values"))

    def entries(self):
        """Alias for values() to mimic older APIs if needed."""
        return self.values()

    def state(self, *state_spec):
        """Get/set widget state (readonly, normal, disabled, etc.)."""
        return super().state(*state_spec)

    # ---------- Undo/Redo ----------

    def _save_state(self):
        current_text = self.get()
        if self._undo_stack and self._undo_stack[-1] == current_text:
            return
        self._redo_stack.clear()
        self._undo_stack.append(current_text)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)

    def _on_key_press(self, event):
        # Skip undo/redo keys from saving state
        if event.keysym.lower() in ("control_z", "control_y"):
            return "break"

        # Only save when editable
        if "readonly" not in self.state():
            self._save_state()
        return ""

    def _do_undo(self, event=None):
        if len(self._undo_stack) <= 1:
            return "break"
        self._redo_stack.append(self.get())
        self._undo_stack.pop()
        prev_text = self._undo_stack[-1]
        self.set(prev_text)
        return "break"

    def _do_redo(self, event=None):
        if not self._redo_stack:
            return "break"
        self._undo_stack.append(self.get())
        next_text = self._redo_stack.pop()
        self.set(next_text)
        return "break"

    # ---------- Paste ----------

    def _custom_paste(self, event):
        if "readonly" in self.state():
            return "break"

        self._save_state()
        try:
            clipboard_text = self.clipboard_get()
            
            # Get current text and cursor position
            current_text = self.get()
            
            # Try to get selection range
            try:
                sel_start = int(self.index("sel.first"))
                sel_end = int(self.index("sel.last"))
                # Delete selected text
                self.tk.call(self._w, "delete", sel_start, sel_end)
                insert_pos = sel_start
            except tk.TclError:
                # No selection, use cursor position
                try:
                    insert_pos = int(self.index("insert"))
                except tk.TclError:
                    insert_pos = len(current_text)
            
            # Insert clipboard text at cursor position using low-level command
            self.tk.call(self._w, "insert", insert_pos, clipboard_text)
            
            # Move cursor after inserted text
            new_cursor_pos = insert_pos + len(clipboard_text)
            self.icursor(new_cursor_pos)
            
            self._redo_stack.clear()
            return "break"
            
        except tk.TclError:
            pass

    # ---------- Select All ----------

    def _select_all(self, event=None):
        self.icursor(tk.END)
        self.selection_range(0, tk.END)
        return "break"

    def _select_all_event(self):
        self._select_all(None)

    # ---------- Deselect ----------

    def deselect(self):
        """Clear selection highlight without changing the text value."""
        try:
            self.tk.call(self._w, "selection", "clear")
        except tk.TclError:
            pass

    def _deselect(self, event=None):
        """Deselect all selected text in the combobox."""
        self.deselect()
        return "break"

    def _deselect_event(self):
        """Context menu wrapper for deselect."""
        self._deselect(None)

    # ---------- Copy/Paste Wrappers (aligned naming) ----------

    def _do_copy_event(self):
        try:
            start = int(self.index("sel.first"))
            end = int(self.index("sel.last"))
            text_to_copy = self.get()[start:end]
        except tk.TclError:
            text_to_copy = self.get()

        self.clipboard_clear()
        self.clipboard_append(text_to_copy)

    def _do_paste_event(self):
        self._custom_paste(None)

    # ---------- Context Menu with Auto-Close (aligned naming) ----------

    def show_menu(self, event):
        self._close_menu()

        x = event.x_root
        y = event.y_root

        if not hasattr(self.menu, "_focus_out_handler_set"):
            self.menu.bind("<FocusOut>", lambda e: self._close_menu())
            self.menu._focus_out_handler_set = True

        self.menu.post(x, y)
        self.menu.focus_set()

        self._menu_timeout_id = self.after(self.MENU_TIMEOUT_MS, self._close_menu)

    def _close_menu(self):
        """Cancel any pending menu timeout and hide the menu if shown."""
        self._cancel_menu_timeout()
        try:
            self.menu.unpost()
        except tk.TclError:
            pass

    def _cancel_menu_timeout(self):
        """Cancel any pending menu auto-close timeout."""
        if self._menu_timeout_id:
            try:
                self.after_cancel(self._menu_timeout_id)
            except tk.TclError:
                pass
            self._menu_timeout_id = None

    def _on_focus_out(self, event=None):
        """Close menu when widget loses focus."""
        self._close_menu()

    # ---------- Combobox-specific behavior ----------

    def _on_combobox_selected(self, event=None):
        # Save state after user picks from dropdown
        self._save_state()

    def destroy(self):
        self._cancel_menu_timeout()
        super().destroy()

class SkiScale(ttk.Frame):
    VERSION = "1.31"

    def __init__(self, parent, **kwargs):
        import time
        self._time = time

        # Custom options
        self._round_places = kwargs.pop('round', 0)
        self._digits = kwargs.pop('digits', 6)
        self._break_limit = kwargs.pop('break_limit', False)
        self._show_entry = kwargs.pop('show_entry', True)

        # Standard Scale options
        self._min_value = float(kwargs.pop('from_'))
        self._max_value = float(kwargs.pop('to', 100))

        self._orient = kwargs.pop('orient', tk.HORIZONTAL)
        self._length = int(kwargs.pop('length', 100))
        self._resolution = float(kwargs.pop('resolution', 1))

        # if self._resolution == 0:
        #     self._resolution = 1
        if self._resolution < 0:
            self._resolution *= -1
        if self._resolution % 1 > 0:
            self._digits += 1

        # Guess decimal rounding if unset.
        if self._round_places == 0 and self._resolution % 1 > 0:
            s = f"{self._resolution:.15f}"
            self._round_places = len(s.split('.')[1].rstrip('0'))

        showvalue = kwargs.pop('showvalue', True)
        self._troughcolor = kwargs.pop('troughcolor', None)
        self._sliderrelief = kwargs.pop('sliderrelief', tk.FLAT)

        self._command_callback = kwargs.pop('command', None)
        self._variable = kwargs.pop('variable', None)
        self._state = kwargs.pop('state', 'active')

        self._value = self._calculate_initial_value()
        self._value_scale = self._clamp_to_range(self._value)

        # Timestamp: ignore slider callbacks until this time (handles animation echoes)
        self._ignore_slider_until = 0.0

        super().__init__(parent, **kwargs)
        self.configure(padding=0)

        self._create_widgets()
        self._setup_bindings()
        self._update_display()

        if self._variable:
            self._variable.trace_add("write", self._on_variable_change)

    @property
    def _true_value(self):
        return self._value

    @_true_value.setter
    def _true_value(self, val):
        self._set_value(val)

    # ========================================================================
    # CORE VALUE LOGIC
    # ========================================================================

    def _calculate_initial_value(self):
        mid = self._min_value + (self._max_value - self._min_value) / 2
        return self._snap_to_step(mid)

    def _clamp_to_range(self, value):
        return max(self._min_value, min(self._max_value, value))

    def _apply_limits(self, value):
        if self._break_limit:
            return self._snap_to_step(value)
        else:
            clamped = self._clamp_to_range(value)
            return self._snap_to_step(clamped)

    def _set_value(self, raw_value, from_slider=False):
        new_value = self._apply_limits(raw_value)

        if new_value != self._value:
            self._value_scale = self._clamp_to_range(new_value)
            self._value = new_value
            if not from_slider:
                self._update_slider_position()
            self._update_entry_display()
            self._notify_command()

        # Update entry color based on break_limit state
        self._update_entry_color()

    def _is_out_of_range(self):
        return self._value < self._min_value or self._value > self._max_value

    # ========================================================================
    # WIDGET CREATION
    # ========================================================================

    def _create_widgets(self):
        orient = self._orient

        self.slider = tk.Scale(
            self,
            orient=orient,
            from_=self._min_value,
            to=self._max_value,
            resolution=self._resolution,
            length=self._length,
            command=self._on_slider_change,
            showvalue=False,
            troughcolor=self._troughcolor or None,
            relief=self._sliderrelief or tk.FLAT,
            state=self._state,
        )

        if self._show_entry:
            self.entry = SkiEntry(
                self,
                width=max(self._digits, 6),
                justify=tk.CENTER,
                font=('TkFixedFont', 9),
                relief=tk.FLAT,
                highlightthickness=0,
                insertbackground='black'
            )
            # Store the default foreground once, so we can restore it later
            self._entry_default_fg = self.entry.cget('foreground')
        else:
            self.entry = None
            self._entry_default_fg = None

        if orient == tk.HORIZONTAL:
            self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if self.entry:
                self.entry.pack(side=tk.RIGHT, padx=0, pady=0)
        else:
            self.slider.pack(side=tk.TOP, fill=tk.Y, expand=True)
            if self.entry:
                self.entry.pack(side=tk.BOTTOM, padx=0, pady=0)

    # ========================================================================
    # EVENT BINDINGS
    # ========================================================================

    def _setup_bindings(self):
        if self.entry:
            self.entry.bind('<FocusOut>', self._on_entry_commit)
            self.entry.bind('<Return>', lambda e: self._on_entry_commit(e))
            self.entry.bind('<KP_Enter>', lambda e: self._on_entry_commit(e))
            self.entry.bind('<Up>', lambda e: self._on_arrow_key(1))
            self.entry.bind('<Down>', lambda e: self._on_arrow_key(-1))

        self.slider.bind('<Up>', lambda e: self._on_arrow_key(1))
        self.slider.bind('<Down>', lambda e: self._on_arrow_key(-1))
        self.slider.bind('<Left>', lambda e: self._on_arrow_key(-1))
        self.slider.bind('<Right>', lambda e: self._on_arrow_key(1))

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def _on_slider_change(self, value_str):
        # Ignore echo callbacks from our own slider.set() animation
        if self._time.time() < self._ignore_slider_until:
            return

        try:
            new_value = float(value_str)
            new_value = self._snap_to_step(new_value)
            self._set_value(new_value, from_slider=True)
        except ValueError:
            pass

    def _on_entry_commit(self, event=None):
        if not self.entry:
            return

        raw = self.entry.get().strip()
        if not raw:
            self._update_entry_display()
            return

        try:
            typed_value = float(raw)
            self._set_value(typed_value)
        except ValueError:
            self._update_entry_display()

    def _on_arrow_key(self, direction):
        current = self._value
        raw_new = current + (direction * self._resolution)
        self._set_value(raw_new)
        return 'break'

    def _on_variable_change(self, *args):
        try:
            new_value = float(self._variable.get())
            self._set_value(new_value)
        except (ValueError, TypeError):
            pass

    # ========================================================================
    # DISPLAY UPDATES
    # ========================================================================

    def _snap_to_step(self, value):
        if self._resolution <= 0:
            return value
        scaled = value / self._resolution
        rounded = round(scaled) * self._resolution
        return round(rounded, 10)

    def _update_slider_position(self):
        """Move the slider. Block echo callbacks for 300ms to cover animation."""
        self._ignore_slider_until = self._time.time() + 0.3

        old_callback = self.slider.cget('command')
        self.slider.configure(command=None)

        try:
            self.slider.set(self._value_scale)
        except tk.TclError:
            pass

        self.slider.configure(command=old_callback)

    def _update_entry_display(self):
        if not self.entry:
            return
        formatted = f"{self._value:.{self._round_places}f}"
        self.entry.delete(0, tk.END)
        self.entry.insert(0, formatted)

    def _update_entry_color(self):
        """Set entry text to red when break_limit is active and value is out of range."""
        if not self.entry or not self._break_limit:
            if self._entry_default_fg is not None:
                self.entry.configure(foreground=self._entry_default_fg)
            return

        if self._is_out_of_range():
            self.entry.configure(foreground='red')
        elif self._entry_default_fg is not None:
            self.entry.configure(foreground=self._entry_default_fg)

    def _update_display(self):
        self._update_slider_position()
        self._update_entry_display()

    def _notify_command(self):
        if self._command_callback:
            try:
                self._command_callback(self._value)
            except Exception:
                pass
        if self._variable:
            try:
                self._variable.set(self._value)
            except Exception:
                pass

    # ========================================================================
    # PUBLIC API
    # ========================================================================

    def get(self):
        return self._value

    def set(self, value):
        try:
            new_value = float(value)
            self._set_value(new_value)
        except (ValueError, TypeError):
            pass

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    def configure(self, cnf=None, **kwargs):
        changed_values = {}

        for key, value in kwargs.items():
            if key == 'from':
                old_value = self._min_value
                self._min_value = float(value)
                self.slider.configure(from_=self._min_value)
                self._value_scale = self._clamp_to_range(self._value)
                self._update_display()
                changed_values['from_'] = (old_value, self._min_value)
            elif key == 'from_':
                old_value = self._min_value
                self._min_value = float(value)
                self.slider.configure(from_=self._min_value)
                self._value_scale = self._clamp_to_range(self._value)
                self._update_display()
                changed_values['from_'] = (old_value, self._min_value)
            elif key == 'to':
                old_value = self._max_value
                self._max_value = float(value)
                self.slider.configure(to=self._max_value)
                self._value_scale = self._clamp_to_range(self._value)
                self._update_display()
                changed_values['to'] = (old_value, self._max_value)
            elif key == 'resolution':
                old_value = self._resolution
                self._resolution = float(value)
                if self._resolution <= 0:
                    self._resolution = abs(self._resolution) or 1
                self.slider.configure(resolution=self._resolution)
                self._value_scale = self._clamp_to_range(self._snap_to_step(self._value))
                self._update_display()
                changed_values['resolution'] = (old_value, self._resolution)
            elif key == 'length':
                old_value = self._length
                self._length = int(value)
                self.slider.configure(length=self._length)
                changed_values['length'] = (old_value, self._length)
            elif key == 'orient':
                old_value = self._orient
                self._orient = value
                self.slider.configure(orient=self._orient)
                self.slider.pack_forget()
                if self.entry:
                    self.entry.pack_forget()
                if self._orient == tk.HORIZONTAL:
                    self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
                    if self.entry:
                        self.entry.pack(side=tk.RIGHT, padx=0, pady=0)
                else:
                    self.slider.pack(side=tk.TOP, fill=tk.Y, expand=True)
                    if self.entry:
                        self.entry.pack(side=tk.BOTTOM, padx=0, pady=0)
                changed_values['orient'] = (old_value, self._orient)
            elif key == 'command':
                self._command_callback = value
                changed_values['command'] = value
            elif key == 'variable':
                if self._variable:
                    try:
                        self._variable.trace_remove("write", self._on_variable_change)
                    except Exception:
                        pass
                self._variable = value
                if self._variable:
                    self._variable.trace_add("write", self._on_variable_change)
                changed_values['variable'] = value
            elif key == 'round':
                self._round_places = int(value)
                self._update_entry_display()
                changed_values['round'] = value
            elif key == 'digits':
                self._digits = int(value)
                if self.entry:
                    self.entry.configure(width=self._digits)
                changed_values['digits'] = value
            elif key == 'break_limit':
                self._break_limit = bool(value)
                changed_values['break_limit'] = value
            elif key == 'show_entry':
                self._show_entry = bool(value)
                changed_values['show_entry'] = value
            elif key == 'state':
                old_value = self._state
                self._state = value
                self.slider.configure(state=self._state)
                changed_values['state'] = (old_value, self._state)
            else:
                try:
                    super().configure(**{key: value})
                    changed_values[key] = value
                except tk.TclError:
                    pass

        return changed_values

    def cget(self, option):
        options = {
            'from_': self._min_value,
            'from': self._min_value,
            'to': self._max_value,
            'orient': self._orient,
            'length': self._length,
            'resolution': self._resolution,
            'command': self._command_callback,
            'variable': self._variable,
            'round': self._round_places,
            'digits': self._digits,
            'break_limit': self._break_limit,
            'show_entry': self._show_entry,
            'state': self._state,
        }
        if option in options:
            return options[option]
        return super().cget(option)

class SkiNotebook(ttk.Frame):
    """
    Drop-in replacement for ttk.Notebook with scrollable tabs, config tab, and locking.

    Rules:
      - max_tabs_visible applies to user tabs only (not arrows/config).
      - 🔒 Locked tabs are always visible.
      - Unlocked tabs are shown as one contiguous window.
      - Total visible user tabs <= max_tabs_visible.
      - (← →) Arrows scroll the unlocked window by ±1.
      - Lock/unlock NEVER changes the scroll position unless it would become invalid.
        In that case, it only clamps to keep the window valid; no recentering/jumping.
      - ⚙ Config tab for debugging and user edits.
    """

    VERSION = "1.07"

    def __init__(self, parent=None, max_tabs_visible=5, config_tab=False, auto_max_tabs=True, debug_mode=False, lock_icon="🔒", unlock_icon="", status_icon="", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(padding=0)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        self._style = ttk.Style()

        self._max_tabs_visible = max(int(max_tabs_visible), 2)
        self._config_tab_enabled = bool(config_tab)
        self._auto_max_tabs = bool(auto_max_tabs)
        self._debug_mode = bool(debug_mode)

        # Customizable icons
        self._lock_icon = str(lock_icon)
        self._unlock_icon = str(unlock_icon)
        self._status_icon = str(status_icon)

        # Configurable guess values for auto calculation
        self._tab_padding = 16
        self._window_margin = 20
        self._min_tab_width = 30

        self._user_tabs = []
        self._child_to_tab = {}

        self._left_arrow_id = None
        self._right_arrow_id = None
        self._config_tab_id = None

        self._last_user_tab = None

        # Scroll index into the UNLOCKED tabs list
        self._unlock_scroll = 0

        self._tab_configs = {}
        
        # Width tracking
        self._tab_widths = {}
        self._debug_width_labels = {}
        
        # Font cache for performance
        self._cached_tab_font = None
        self._cached_font_name = None

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.bind("<Configure>", self._on_configure)

        self._create_left_arrow()
        if self._config_tab_enabled:
            self._create_config_tab()
        
        self._recalculate_auto_max_tabs()
        self._sync_config_colors()

    def _get_all_tabs_in_order(self):
        """Return all tabs (user + special) in notebook order."""
        return list(self.notebook.tabs())

    def _recalculate_tab_width(self, tid):
        """Recalculate and store the width for a single tab using FULL display name."""
        width = self._get_tab_label_width(tid)
        self._tab_widths[tid] = width
        
        if self._debug_mode and tid in getattr(self, '_debug_width_labels', {}):
            self._debug_width_labels[tid].config(text=f"{width}px")

    def _recalculate_all_tab_widths(self):
        """Recalculate widths for all tabs. Call when structure changes."""
        all_tabs = self._get_all_tabs_in_order()
        total = 0
        for tid in all_tabs:
            width = self._get_tab_label_width(tid)
            self._tab_widths[tid] = width
            total += width
        return total

    def _get_tab_label_width(self, tid):
        """Get the pixel width of a tab's FULL display label text (including lock/status icons)."""
        try:
            # Get the FULL display text as shown on the tab
            text = self.notebook.tab(tid, "text")
        except tk.TclError:
            return 0
        
        if not text:
            return 0
                
        font_obj = self._detect_tab_font()
        width = font_obj.measure(text)
        width += self._tab_padding
        
        return max(width, self._min_tab_width)

    def _get_available_tab_space(self):
        """Calculate available horizontal space for tabs in pixels."""
        if not self.winfo_viewable():
            return 0
            
        total_width = self.winfo_width()
        if total_width <= 0:
            return 0
        
        available = total_width - self._window_margin
        return max(available, 0)

    def _find_max_tabs_that_fit_from_start(self, start_index, user_tabs_only=True):
        """Starting from start_index, find how many consecutive tabs fit in available space."""
        all_tabs = self._get_all_tabs_in_order()
        if start_index >= len(all_tabs):
            return (0, 0)
        
        available = self._get_available_tab_space()
        total_width = 0
        count = 0
        
        for i in range(start_index, len(all_tabs)):
            tid = all_tabs[i]
            
            if user_tabs_only and self._is_special(tid):
                continue
            
            tab_width = self._tab_widths.get(tid, self._get_tab_label_width(tid))
            
            if total_width + tab_width > available:
                break
            
            total_width += tab_width
            count += 1
        
        return (count, total_width)

    def _recalculate_auto_max_tabs(self):
        """Recalculate max_tabs_visible by finding how many visible tabs fit."""
        if not self._auto_max_tabs:
            return
        
        available_space = self._get_available_tab_space()
        if available_space <= 0:
            return
        
        unlocked = self._unlocked_tabs()
        locked_count = self._locked_count()
        room = max(self._max_tabs_visible - locked_count, 0)
        start = self._unlock_scroll
        end = min(start + room, len(unlocked))
        
        visible_unlocked = unlocked[start:end]
        
        total_visible_width = 0
        for tid in self._user_tabs:
            if self._is_locked(tid) or tid in visible_unlocked:
                width = self._tab_widths.get(tid, self._get_tab_label_width(tid))
                total_visible_width += width
        
        num_visible = locked_count + len(visible_unlocked)
        
        if num_visible > 0:
            avg_visible_width = total_visible_width / num_visible
            tabs_that_fit = int(available_space / avg_visible_width)
        else:
            tabs_that_fit = self._max_tabs_visible
        
        calculated_max = max(tabs_that_fit, 2)
        
        old_max = self._max_tabs_visible
        self._max_tabs_visible = calculated_max
        
        if calculated_max < old_max:
            self._clamp_unlock_scroll()
        
        self._apply_visibility_window("AutoMaxRecalc")
        
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()

    def _on_configure(self, event=None):
        """Handle window resize events - also clears font cache."""
        self._cached_tab_font = None
        self._cached_font_name = None
        
        self._sync_config_colors()

        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()

    def _is_arrow(self, tid):
        return tid == self._left_arrow_id or tid == self._right_arrow_id

    def _is_special(self, tid):
        return self._is_arrow(tid) or tid == self._config_tab_id

    def _normalize_tab_id(self, tid):
        if tid is None:
            return None

        all_tabs = self.notebook.tabs()
        if tid in all_tabs:
            if not self._is_special(tid):
                return tid
            return None

        if tid in self._child_to_tab:
            candidate = self._child_to_tab[tid]
            if candidate in all_tabs and not self._is_special(candidate):
                return candidate
            return None

        if isinstance(tid, int):
            idx = tid
            n = len(all_tabs)
            if idx < 0:
                idx += n
            if 0 <= idx < n:
                real_tid = all_tabs[idx]
                if not self._is_special(real_tid):
                    return real_tid
            return None

        try:
            idx = self.notebook.index(tid)
        except tk.TclError:
            return None
        n = len(all_tabs)
        if 0 <= idx < n:
            real_tid = all_tabs[idx]
            if not self._is_special(real_tid):
                return real_tid
        return None

    def _ensure_in_user_tabs(self, tid):
        if tid in self._user_tabs:
            return
        try:
            self.notebook.index(tid)
        except tk.TclError:
            return
        if self._is_special(tid):
            return
        user_idx = 0
        for t in self.notebook.tabs():
            if t == tid:
                break
            if not self._is_special(t) and t in self._user_tabs:
                user_idx += 1
        if user_idx >= len(self._user_tabs):
            self._user_tabs.append(tid)
        else:
            self._user_tabs.insert(user_idx, tid)
        if tid not in self._tab_configs:
            try:
                current_text = self.notebook.tab(tid, "text")
            except tk.TclError:
                current_text = ""
            self._tab_configs[tid] = {
                "name": str(current_text or ""),
                "locked": False,
                "status": "",
            }
        self._apply_tab_label(tid)
        
        self._recalculate_tab_width(tid)

    def _apply_tab_label(self, tid):
        """Apply the FULL display name to the tab (lock icon + base name + status)."""
        cfg = self._tab_configs.get(tid, {})
        name = cfg.get("name", "") or ""
        locked = bool(cfg.get("locked", False))
        status = cfg.get("status", "") or ""
        
        # Build full display name: <lock_icon> + <base_name> + <status>
        lock_prefix = self._lock_icon if locked else self._unlock_icon
        display = f"{lock_prefix}{name}{status}".rstrip()
        
        try:
            self.notebook.tab(tid, text=display)
        except tk.TclError:
            pass

    # ==========================================================================
    # EXPOSED LOCK/UNLOCK FUNCTIONS (PUBLIC API)
    # ==========================================================================

    def lock_tab(self, tab_id):
        """Lock a tab. Returns True if successful, False if max locks reached."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return False
        
        cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
        
        if cfg["locked"]:
            return True  # Already locked
        
        n_locked_now = self._locked_count()
        if n_locked_now >= self._max_locks():
            return False  # Max locks reached
        
        cfg["locked"] = True
        self._apply_tab_label(tid)
        self._clamp_unlock_scroll()
        self._apply_visibility_window("LockChange")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def unlock_tab(self, tab_id):
        """Unlock a tab. Returns True if successful."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return False
        
        cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
        
        if not cfg["locked"]:
            return True  # Already unlocked
        
        cfg["locked"] = False
        self._apply_tab_label(tid)
        self._clamp_unlock_scroll()
        self._apply_visibility_window("UnlockChange")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def toggle_lock(self, tab_id):
        """Toggle lock state of a tab. Returns new lock state."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return False
        
        cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
        
        if cfg["locked"]:
            self.unlock_tab(tid)
            return False
        else:
            result = self.lock_tab(tid)
            return result if result else False

    # ==========================================================================
    # EXPOSED SET NAME FUNCTION (PUBLIC API - sets base_name only)
    # ==========================================================================

    def set_tab_name(self, tab_id, name):
        """Set the base name of a tab (without lock/status icons)."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return False
        
        cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
        cfg["name"] = str(name)
        
        self._apply_tab_label(tid)
        self._recalculate_tab_width(tid)
        
        if self._debug_mode and tid in getattr(self, '_debug_width_labels', {}):
            width = self._tab_widths.get(tid, 0)
            self._debug_width_labels[tid].config(text=f"{width}px")
            
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def get_tab_name(self, tab_id):
        """Get the base name of a tab (without lock/status icons)."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return None
        
        cfg = self._tab_configs.get(tid, {})
        return cfg.get("name", "")

    # ==========================================================================
    # EXPOSED SET STATUS FUNCTION (PUBLIC API)
    # ==========================================================================

    def set_tab_status(self, tab_id, status):
        """Set the status indicator of a tab (appended to display name)."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return False
        
        cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
        cfg["status"] = str(status)
        
        self._apply_tab_label(tid)
        self._recalculate_tab_width(tid)
        
        if self._debug_mode and tid in getattr(self, '_debug_width_labels', {}):
            width = self._tab_widths.get(tid, 0)
            self._debug_width_labels[tid].config(text=f"{width}px")
            
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def get_tab_status(self, tab_id):
        """Get the status indicator of a tab."""
        tid = self._normalize_tab_id(tab_id)
        if tid is None or self._is_special(tid):
            return None
        
        cfg = self._tab_configs.get(tid, {})
        return cfg.get("status", "")

    # ==========================================================================
    # ICON CONFIGURATION (PUBLIC API)
    # ==========================================================================

    def set_lock_icon(self, icon):
        """Set custom lock icon character."""
        old_icon = self._lock_icon
        self._lock_icon = str(icon)
        
        # Update all locked tabs' display
        for tid in self._user_tabs:
            if self._is_locked(tid):
                self._apply_tab_label(tid)
                self._recalculate_tab_width(tid)
                
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        return old_icon

    def set_unlock_icon(self, icon):
        """Set custom unlock icon character."""
        old_icon = self._unlock_icon
        self._unlock_icon = str(icon)
        
        # Update all unlocked tabs' display
        for tid in self._user_tabs:
            if not self._is_locked(tid):
                self._apply_tab_label(tid)
                self._recalculate_tab_width(tid)
                
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        return old_icon

    def set_status_icon(self, icon):
        """Set custom status icon character."""
        old_icon = self._status_icon
        self._status_icon = str(icon)
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        return old_icon

    def get_lock_icon(self):
        """Get current lock icon."""
        return self._lock_icon

    def get_unlock_icon(self):
        """Get current unlock icon."""
        return self._unlock_icon

    def get_status_icon(self):
        """Get current status icon."""
        return self._status_icon

    # ==========================================================================
    # LOCK HELPERS
    # ==========================================================================

    def _is_locked(self, tid):
        cfg = self._tab_configs.get(tid, {})
        return bool(cfg.get("locked", False))

    def _locked_count(self):
        return sum(1 for c in self._tab_configs.values() if c["locked"])

    def _max_locks(self):
        return max(self._max_tabs_visible - 1, 0)

    # ==========================================================================
    # ARROW & CONFIG TAB MANAGEMENT
    # ==========================================================================

    def _create_left_arrow(self):
        lf = ttk.Frame(self.notebook)
        raw_id = self.notebook.add(lf, text="←")
        all_tabs = self.notebook.tabs()
        self._left_arrow_id = all_tabs[-1] if all_tabs else raw_id
        self.notebook.hide(self._left_arrow_id)
        self._recalculate_tab_width(self._left_arrow_id)

    def _create_config_tab(self):
        if not self._config_tab_enabled:
            return
        if self._config_tab_id is not None:
            try:
                self.notebook.forget(self._config_tab_id)
            except tk.TclError:
                pass
            self._config_tab_id = None

        cf = ttk.Frame(self.notebook)
        self._build_config_ui(cf)
        raw_id = self.notebook.add(cf, text="⚙")
        all_tabs = self.notebook.tabs()
        self._config_tab_id = all_tabs[-1] if all_tabs else raw_id
        self.notebook.hide(self._config_tab_id)
        self._recalculate_tab_width(self._config_tab_id)

    def _ensure_right_arrow_at_end(self):
        if self._right_arrow_id is not None:
            try:
                self.notebook.forget(self._right_arrow_id)
            except tk.TclError:
                pass
            self._right_arrow_id = None

        rf = ttk.Frame(self.notebook)
        self.notebook.add(rf, text="→")
        all_tabs = self.notebook.tabs()
        self._right_arrow_id = all_tabs[-1] if all_tabs else None
        if self._right_arrow_id is not None:
            self.notebook.hide(self._right_arrow_id)
            self._recalculate_tab_width(self._right_arrow_id)

    def _remove_right_arrow(self):
        if self._right_arrow_id is not None:
            try:
                self.notebook.forget(self._right_arrow_id)
            except tk.TclError:
                pass
            self._right_arrow_id = None

    # ==========================================================================
    # CONFIG UI
    # ==========================================================================

    def _build_config_ui(self, parent_frame):
        for w in parent_frame.winfo_children():
            w.destroy()

        bg_color = self._get_notebook_tab_background()
        
        canvas = tk.Canvas(parent_frame, 
                           highlightthickness=0,
                           bg=bg_color,
                           relief=tk.FLAT)
        
        scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        inner = tk.Frame(canvas, bg=bg_color)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner.bind("<Configure>", on_frame_configure)
        parent_frame.bind("<Configure>", on_frame_configure)

        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)

        self._config_inner = inner
        self._config_canvas = canvas
        self._config_parent = parent_frame
        
        self._refresh_config_items()

    def _refresh_config_items(self):
        if not hasattr(self, "_config_inner"):
            return

        for w in self._config_inner.winfo_children():
            w.destroy()

        # ==========================================================================
        # DEBUG INFO ROW (only shown when debug_mode is True)
        # ==========================================================================
        if self._debug_mode:
            debug_row = ttk.Frame(self._config_inner)
            debug_row.pack(fill=tk.X, padx=0, pady=0)
            
            total_width = sum(self._tab_widths.values())
            available = self._get_available_tab_space()
            
            ttk.Label(debug_row, text=f"DEBUG: Available={available}px, Total tabs={total_width}px, Visible count={self._max_tabs_visible}", 
                     foreground="blue").pack(side=tk.LEFT, padx=0, pady=0)
            
            debug_row2 = ttk.Frame(self._config_inner)
            debug_row2.pack(fill=tk.X, padx=0, pady=0)

            font_obj = self._detect_tab_font()
            try:
                font_name = font_obj.actual()
                font_size = font_obj.cget('size')
                font_info = f"Tab Font: {font_name} [{font_size}pt]"
            except tk.TclError:
                font_info = f"Tab Font: {str(font_obj)}"
            
            ttk.Label(debug_row2, text=font_info, foreground="green").pack(side=tk.LEFT, padx=0, pady=0)
            
            if self._cached_tab_font is not None:
                ttk.Label(debug_row, text="[CACHED]", foreground="cyan").pack(side=tk.LEFT, padx=0, pady=0)
            else:
                ttk.Label(debug_row, text="[MISS]", foreground="red").pack(side=tk.LEFT, padx=0, pady=0)

        # ==========================================================================
        # ICON SETTINGS GROUP (NEW - GLOBAL ICON CONFIGURATION)
        # ==========================================================================
        icon_settings_group = ttk.LabelFrame(self._config_inner, text="Icon Settings", padding=2)
        icon_settings_group.pack(fill=tk.X, padx=0, pady=2)

        icon_row = ttk.Frame(icon_settings_group)
        icon_row.pack(fill=tk.X, padx=0, pady=2)

        ttk.Label(icon_row, text="Lock Icon:").pack(side=tk.LEFT, padx=0, pady=0)
        lock_icon_var = tk.StringVar(value=self._lock_icon)
        
        def on_lock_icon_changed(event=None):
            new_icon = lock_icon_var.get().strip()
            if new_icon:
                self.set_lock_icon(new_icon)
        
        lock_icon_entry = SkiEntry(icon_row, textvariable=lock_icon_var, width=4)
        lock_icon_entry.pack(side=tk.LEFT, padx=2, pady=0)
        lock_icon_entry.bind("<Return>", on_lock_icon_changed)
        lock_icon_entry.bind("<FocusOut>", on_lock_icon_changed)

        ttk.Label(icon_row, text="Unlock Icon:").pack(side=tk.LEFT, padx=10, pady=0)
        unlock_icon_var = tk.StringVar(value=self._unlock_icon)
        
        def on_unlock_icon_changed(event=None):
            new_icon = unlock_icon_var.get().strip()
            if new_icon:
                self.set_unlock_icon(new_icon)
        
        unlock_icon_entry = SkiEntry(icon_row, textvariable=unlock_icon_var, width=4)
        unlock_icon_entry.pack(side=tk.LEFT, padx=2, pady=0)
        unlock_icon_entry.bind("<Return>", on_unlock_icon_changed)
        unlock_icon_entry.bind("<FocusOut>", on_unlock_icon_changed)

        # ==========================================================================
        # AUTO MAX TABS SETTINGS GROUP (with border)
        # ==========================================================================
        auto_settings_group = ttk.LabelFrame(self._config_inner, text="Auto Max Tabs Settings", padding=2)
        auto_settings_group.pack(fill=tk.X, padx=0, pady=2)

        row1 = ttk.Frame(auto_settings_group)
        row1.pack(fill=tk.X, padx=0, pady=2)

        ttk.Label(row1, text="Auto Max:").pack(side=tk.LEFT, padx=0, pady=0)
        
        auto_var = tk.BooleanVar(value=self._auto_max_tabs)
        
        def on_auto_changed(event=None):
            self._auto_max_tabs = bool(auto_var.get())
            if self._auto_max_tabs:
                self._recalculate_auto_max_tabs()
        
        auto_check = ttk.Checkbutton(row1, variable=auto_var, command=on_auto_changed)
        auto_check.pack(side=tk.LEFT, padx=5, pady=0)

        ttk.Label(row1, text="Tabs Visible:").pack(side=tk.LEFT, padx=10, pady=0)

        max_var = tk.StringVar(value=str(self._max_tabs_visible))

        def on_max_changed(event=None):
            try:
                val = int(max_var.get())
            except ValueError:
                return
            new_val = max(val, 2)
            old_val = self._max_tabs_visible
            self._max_tabs_visible = new_val
            max_var.set(str(new_val))
            if new_val != old_val:
                self._clamp_unlock_scroll()
                self._apply_visibility_window("MaxTabsChanged")

        max_entry = SkiEntry(row1, textvariable=max_var, width=2)
        max_entry.pack(side=tk.LEFT, padx=5, pady=0)
        max_entry.bind("<Return>", on_max_changed)
        max_entry.bind("<FocusOut>", on_max_changed)

        row2 = ttk.Frame(auto_settings_group)
        row2.pack(fill=tk.X, padx=0, pady=2)

        ttk.Label(row2, text="Tab Padding:").pack(side=tk.LEFT, padx=0, pady=0)
        tab_padding_var = tk.StringVar(value=str(self._tab_padding))
        
        def on_tab_padding_changed(event=None):
            try:
                val = int(tab_padding_var.get())
            except ValueError:
                return
            self._tab_padding = max(val, 0)
            tab_padding_var.set(str(self._tab_padding))
            self._recalculate_all_tab_widths()
            if self._auto_max_tabs:
                self._recalculate_auto_max_tabs()
        
        tab_padding_entry = SkiEntry(row2, textvariable=tab_padding_var, width=2)
        tab_padding_entry.pack(side=tk.LEFT, padx=2, pady=0)
        tab_padding_entry.bind("<Return>", on_tab_padding_changed)
        tab_padding_entry.bind("<FocusOut>", on_tab_padding_changed)

        ttk.Label(row2, text="Window Margin:").pack(side=tk.LEFT, padx=10, pady=0)
        window_margin_var = tk.StringVar(value=str(self._window_margin))
        
        def on_window_margin_changed(event=None):
            try:
                val = int(window_margin_var.get())
            except ValueError:
                return
            self._window_margin = max(val, 0)
            window_margin_var.set(str(self._window_margin))
            if self._auto_max_tabs:
                self._recalculate_auto_max_tabs()
        
        window_margin_entry = SkiEntry(row2, textvariable=window_margin_var, width=2)
        window_margin_entry.pack(side=tk.LEFT, padx=2, pady=0)
        window_margin_entry.bind("<Return>", on_window_margin_changed)
        window_margin_entry.bind("<FocusOut>", on_window_margin_changed)

        row3 = ttk.Frame(auto_settings_group)
        row3.pack(fill=tk.X, padx=0, pady=2)

        ttk.Label(row3, text="Min Tab Width:").pack(side=tk.LEFT, padx=0, pady=0)
        min_width_var = tk.StringVar(value=str(self._min_tab_width))
        
        def on_min_width_changed(event=None):
            try:
                val = int(min_width_var.get())
            except ValueError:
                return
            self._min_tab_width = max(val, 10)
            min_width_var.set(str(self._min_tab_width))
            self._recalculate_all_tab_widths()
            if self._auto_max_tabs:
                self._recalculate_auto_max_tabs()
        
        min_width_entry = SkiEntry(row3, textvariable=min_width_var, width=2)
        min_width_entry.pack(side=tk.LEFT, padx=2, pady=0)
        min_width_entry.bind("<Return>", on_min_width_changed)
        min_width_entry.bind("<FocusOut>", on_min_width_changed)

        # ==========================================================================
        # TAB SETTINGS GROUP (with border)
        # ==========================================================================
        tab_settings_group = ttk.LabelFrame(self._config_inner, text="Tab Settings", padding=2)
        tab_settings_group.pack(fill=tk.X, padx=0, pady=2)

        for idx, tid in enumerate(self._user_tabs):
            cfg = self._tab_configs.get(tid, {"name": "", "locked": False, "status": ""})
            row = ttk.Frame(tab_settings_group)
            row.pack(fill=tk.X, padx=0, pady=2)

            name_var = tk.StringVar(value=cfg.get("name", ""))
            status_var = tk.StringVar(value=cfg.get("status", ""))
            lock_state = bool(cfg.get("locked", False))

            ttk.Label(row, text=f"#{idx + 1}", width=3).pack(side=tk.LEFT, padx=0, pady=0)
            name_entry = SkiEntry(row, textvariable=name_var, width=16)
            name_entry.pack(side=tk.LEFT, padx=2, pady=0)

            lock_btn = ttk.Button(row, text=self._lock_icon if lock_state else self._unlock_icon, width=2)
            lock_btn.pack(side=tk.LEFT, padx=2, pady=0)

            status_entry = SkiEntry(row, textvariable=status_var, width=4)
            status_entry.pack(side=tk.LEFT, padx=2, pady=0)

            if self._debug_mode:
                width_val = self._tab_widths.get(tid, 0)
                width_label = ttk.Label(row, text=f"{width_val}px", width=6, foreground="gray")
                width_label.pack(side=tk.LEFT, padx=2, pady=0)
                self._debug_width_labels[tid] = width_label

            def make_lock_callback(tid=tid, btn=lock_btn):
                def cb():
                    c = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
                    if c["locked"]:
                        c["locked"] = False
                        btn.config(text=self._unlock_icon)
                    else:
                        n_locked_now = self._locked_count()
                        if n_locked_now >= self._max_locks():
                            return
                        c["locked"] = True
                        btn.config(text=self._lock_icon)
                    self._apply_tab_label(tid)
                    self._clamp_unlock_scroll()
                    self._apply_visibility_window("LockChange")
                return cb

            lock_btn.config(command=make_lock_callback())

            def make_name_apply(name_var=name_var, tid=tid):
                def cb(event=None):
                    new_name = name_var.get().strip()
                    cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
                    cfg["name"] = new_name
                    self._apply_tab_label(tid)
                    self._recalculate_tab_width(tid)
                    if self._debug_mode and tid in getattr(self, '_debug_width_labels', {}):
                        width = self._tab_widths.get(tid, 0)
                        self._debug_width_labels[tid].config(text=f"{width}px")
                    if self._auto_max_tabs:
                        self._recalculate_auto_max_tabs()
                return cb

            name_entry.bind("<Return>", make_name_apply())
            name_entry.bind("<FocusOut>", make_name_apply())

            def make_status_apply(status_var=status_var, tid=tid):
                def cb(event=None):
                    new_status = status_var.get().strip()
                    cfg = self._tab_configs.setdefault(tid, {"name": "", "locked": False, "status": ""})
                    cfg["status"] = new_status
                    self._apply_tab_label(tid)
                    self._recalculate_tab_width(tid)
                    if self._debug_mode and tid in getattr(self, '_debug_width_labels', {}):
                        width = self._tab_widths.get(tid, 0)
                        self._debug_width_labels[tid].config(text=f"{width}px")
                    if self._auto_max_tabs:
                        self._recalculate_auto_max_tabs()
                return cb

            status_entry.bind("<Return>", make_status_apply())
            status_entry.bind("<FocusOut>", make_status_apply())

    def _detect_tab_font(self):
        """Detect the actual font being used by notebook tabs."""
        if self._cached_tab_font is not None:
            return self._cached_tab_font
        
        font_obj = None
        font_name = None
        
        try:
            font_name = self.notebook.cget('font')
            if font_name and isinstance(font_name, str) and font_name.strip():
                font_obj = font.nametofont(font_name)
        except tk.TclError:
            pass
        
        if font_obj is None:
            try:
                style_config = self.notebook.style.lookup("TNotebook.Tab", 'font', False)
                if style_config and isinstance(style_config, str) and style_config.strip():
                    font_obj = font.nametofont(style_config)
            except Exception:
                pass
        
        if font_obj is None:
            try:
                parent_font = self.cget('font')
                if parent_font and isinstance(parent_font, str) and parent_font.strip():
                    font_obj = font.nametofont(parent_font)
            except tk.TclError:
                pass
        
        if font_obj is None:
            font_obj = font.nametofont('TkDefaultFont')
        
        self._cached_tab_font = font_obj
        
        try:
            self._cached_font_name = font_obj.actual()
        except tk.TclError:
            self._cached_font_name = str(font_obj)
        
        return font_obj

    def _get_notebook_tab_background(self):
        """Get the background color for config tab."""
        try:
            bg = self._style.lookup('TNotebook', 'background', False)
            if not bg or not bg.strip():
                bg = self._style.lookup('TFrame', 'background', False)
            if bg and bg.strip():
                return bg
        except tk.TclError:
            pass
        
        return 'white'

    def _sync_config_colors(self):
        """Sync config tab colors with notebook theme."""
        if not hasattr(self, '_config_canvas'):
            return
            
        bg_color = self._get_notebook_tab_background()
        
        self._config_canvas.configure(bg=bg_color)
        
        if hasattr(self, '_config_inner'):
            self._config_inner.configure(bg=bg_color)
        
        if hasattr(self, '_config_inner'):
            for widget in self._config_inner.winfo_children():
                try:
                    widget.configure(bg=bg_color)
                except tk.TclError:
                    pass

    def _update_config_icon_entries(self):
        """Update config tab icon entry fields when icons are changed."""
        if not hasattr(self, "_config_inner"):
            return
        
        # Find and update lock/unlock/status icon entries if they exist
        for widget in self._config_inner.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget("text") == "Icon Settings":
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for entry in child.winfo_children():
                            if isinstance(entry, SkiEntry):
                                # Check variable name or position to determine which entry
                                var = entry.cget("textvariable")
                                if var and hasattr(var, 'get'):
                                    # This won't work directly, need different approach
                                    pass

    # ==========================================================================
    # VISIBILITY LOGIC
    # ==========================================================================

    def _unlocked_tabs(self):
        return [t for t in self._user_tabs if not self._is_locked(t)]

    def _clamp_unlock_scroll(self):
        """Keep _unlock_scroll valid after lock/unlock or structural changes."""
        unlocked = self._unlocked_tabs()
        n_unlocked = len(unlocked)
        locked_count = self._locked_count()
        room = max(self._max_tabs_visible - locked_count, 0)

        max_start = max(n_unlocked - room, 0)

        if self._unlock_scroll < 0:
            self._unlock_scroll = 0
        elif self._unlock_scroll > max_start:
            self._unlock_scroll = max_start

    def _apply_visibility_window(self, reason=""):
        unlocked = self._unlocked_tabs()
        n_unlocked = len(unlocked)
        locked_count = self._locked_count()
        room = max(self._max_tabs_visible - locked_count, 0)

        start = self._unlock_scroll
        end = min(start + room, n_unlocked)

        visible_unlocked_ids = set(unlocked[start:end])

        for tid in self._user_tabs:
            if self._is_locked(tid):
                try:
                    self.notebook.tab(tid, state="normal")
                except tk.TclError:
                    pass
            elif tid in visible_unlocked_ids:
                try:
                    self.notebook.tab(tid, state="normal")
                except tk.TclError:
                    pass
            else:
                try:
                    self.notebook.hide(tid)
                except tk.TclError:
                    pass

        show_left = start > 0
        show_right = end < n_unlocked

        if self._left_arrow_id is not None:
            if show_left:
                try:
                    self.notebook.tab(self._left_arrow_id, state="normal")
                except tk.TclError:
                    pass
            else:
                try:
                    self.notebook.hide(self._left_arrow_id)
                except tk.TclError:
                    pass

        if self._config_tab_enabled and self._config_tab_id is not None:
            try:
                self.notebook.tab(self._config_tab_id, state="normal")
            except tk.TclError:
                pass

        if show_right:
            self._ensure_right_arrow_at_end()
            if self._right_arrow_id is not None:
                try:
                    self.notebook.tab(self._right_arrow_id, state="normal")
                except tk.TclError:
                    pass
        else:
            self._remove_right_arrow()

    def _refresh_visibility_from_selection(self, reason=""):
        self._clamp_unlock_scroll()
        self._apply_visibility_window(reason)

    # ==========================================================================
    # ARROW CLICKS
    # ==========================================================================

    def _on_arrow_click(self, direction):
        unlocked = self._unlocked_tabs()
        n_unlocked = len(unlocked)
        locked_count = self._locked_count()
        room = max(self._max_tabs_visible - locked_count, 0)

        if room <= 0 or n_unlocked <= room:
            return

        start = self._unlock_scroll
        end = min(start + room, n_unlocked)

        if direction == 1:
            if end >= n_unlocked:
                return
            new_start = min(start + 1, n_unlocked - room)
        else:
            if start <= 0:
                return
            new_start = max(start - 1, 0)

        self._unlock_scroll = new_start
        self._apply_visibility_window("ArrowScroll")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()

        if not self._last_user_tab or self._is_locked(self._last_user_tab):
            if unlocked and new_start < n_unlocked:
                target = unlocked[new_start]
                self._last_user_tab = target
                self.notebook.select(target)
            return

        try:
            cur_idx_u = unlocked.index(self._last_user_tab)
        except ValueError:
            cur_idx_u = -1

        new_end = min(new_start + room, n_unlocked)

        if cur_idx_u < new_start:
            target = unlocked[new_start]
        elif cur_idx_u >= new_end:
            target = unlocked[new_end - 1]
        else:
            target = self._last_user_tab

        if target != self._last_user_tab:
            self._last_user_tab = target
            self.notebook.select(target)

    # ==========================================================================
    # EVENTS & PUBLIC API
    # ==========================================================================

    def _on_tab_changed(self, event=None):
        current = self.notebook.select()
        if not current:
            return
        if self._is_arrow(current):
            direction = 1 if current == self._right_arrow_id else -1
            self._on_arrow_click(direction)
            if self._user_tabs and self._last_user_tab:
                self.notebook.select(self._last_user_tab)
        elif current == self._config_tab_id:
            self._refresh_config_items()
        elif current in self._user_tabs:
            self._last_user_tab = current

    def add(self, child, **kw):
        text = kw.pop('text', 'Tab')
        raw_tid = self.notebook.add(child, text=text, **kw)
        all_tabs = self.notebook.tabs()
        tid = all_tabs[-1] if all_tabs else raw_tid
        self._child_to_tab[child] = tid

        self._ensure_in_user_tabs(tid)

        if self._last_user_tab is None or self._last_user_tab not in self._user_tabs:
            self._last_user_tab = tid

        self._refresh_visibility_from_selection("AfterAdd")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()

        return tid

    def _user_index_to_notebook_index(self, index):
        all_tabs = self.notebook.tabs()
        if not isinstance(index, int):
            return index

        n_users = len(self._user_tabs)
        if index < 0:
            index = max(0, n_users + index)
        elif index > n_users:
            index = n_users

        user_count = 0
        for tid in all_tabs:
            if self._is_special(tid):
                continue
            if user_count == index:
                return all_tabs.index(tid)
            user_count += 1

        if self._right_arrow_id is not None:
            return self.notebook.index(self._right_arrow_id)
        return len(all_tabs)

    def tabs(self):
        all_tabs = self.notebook.tabs()
        return [t for t in all_tabs if not self._is_special(t)]

    def insert(self, index, child, **kw):
        text = kw.pop('text', 'Tab')
        real_index = self._user_index_to_notebook_index(index)
        raw_tid = self.notebook.insert(real_index, child, text=text, **kw)
        all_tabs = self.notebook.tabs()
        tid = all_tabs[-1] if all_tabs else raw_tid
        self._child_to_tab[child] = tid

        if isinstance(index, str):
            idx = next(
                (i for i, t in enumerate(self._user_tabs) if t == index),
                len(self._user_tabs),
            )
        else:
            idx = max(0, min(int(index), len(self._user_tabs)))

        self._user_tabs = [t for t in self._user_tabs if t != tid]
        self._user_tabs.insert(idx, tid)

        if self._last_user_tab is None or self._last_user_tab not in self._user_tabs:
            self._last_user_tab = tid

        self._refresh_visibility_from_selection("AfterInsert")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
        return tid

    def remove(self, s):
        """Remove a tab. Returns False if tab is locked (cannot be removed)."""
        tid = self._normalize_tab_id(s)
        if tid is None or self._is_special(tid):
            return False
        
        # Locked tabs cannot be removed via remove()
        if self._is_locked(tid):
            return False
            
        try:
            child = self.notebook.tab(tid, "child")
            self._child_to_tab.pop(child, None)
            self.notebook.remove(tid)
        except tk.TclError:
            pass
        removed_was_last = self._last_user_tab == tid
        self._user_tabs = [t for t in self._user_tabs if t != tid]
        self._tab_configs.pop(tid, None)
        self._tab_widths.pop(tid, None)

        if removed_was_last:
            self._last_user_tab = self._user_tabs[0] if self._user_tabs else None

        self._clamp_unlock_scroll()
        self._apply_visibility_window("AfterRemove")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def forget(self, s):
        tid = self._normalize_tab_id(s)
        if tid is None or self._is_special(tid):
            return False
        
        # Locked tabs cannot be forgotten via forget()
        if self._is_locked(tid):
            return False
            
        try:
            self.notebook.forget(tid)
        except tk.TclError:
            pass
            
        removed_was_last = self._last_user_tab == tid
        self._user_tabs = [t for t in self._user_tabs if t != tid]
        self._tab_configs.pop(tid, None)
        self._tab_widths.pop(tid, None)

        if removed_was_last:
            self._last_user_tab = self._user_tabs[0] if self._user_tabs else None

        self._clamp_unlock_scroll()
        self._apply_visibility_window("AfterForget")
        
        if self._auto_max_tabs:
            self._recalculate_auto_max_tabs()
            
        if self._config_tab_enabled and hasattr(self, "_config_inner"):
            self._refresh_config_items()
            
        return True

    def tab(self, *args, **kwargs):
        """
        Match ttk.Notebook.tab(tab_id [, option=value...]):
          - tab(tab_id)               -> query all options (dict)
          - tab(tab_id, option)       -> query single option
          - tab(tab_id, opt=val, ...) -> set option(s) and return ""
        Supports int index from .index(), widget child, or tab id.
        When setting 'text', it sets the base_name only.
        """
        if len(args) == 0 and "tab_id" in kwargs:
            tid_arg = kwargs.pop("tab_id")
            args = (tid_arg,) + args

        if len(args) < 1:
            raise tk.TclError("missing tab id")

        tid_arg = args[0]
        real_tid = self._normalize_tab_id(tid_arg)
        if real_tid is None:
            raise tk.TclError("invalid tab id")
        if self._is_special(real_tid):
            return {}

        opts_to_set = {k: v for k, v in kwargs.items()}
        query_option = None

        if len(args) >= 2 and not kwargs:
            query_option = args[1]
        elif kwargs or (len(args) >= 2):
            pass

        if query_option is not None:
            # Query mode: if querying 'text', return base_name only
            if query_option == "text":
                cfg = self._tab_configs.get(real_tid, {})
                return cfg.get("name", "")
            result = self.notebook.tab(real_tid, query_option)
            return result

        if opts_to_set:
            # Set mode: handle 'text' specially to set base_name only
            if "text" in opts_to_set:
                cfg = self._tab_configs.setdefault(real_tid, {"name": "", "locked": False, "status": ""})
                new_text = str(opts_to_set["text"])
                cfg["name"] = new_text
                # Recalculate width for this tab
                self._recalculate_tab_width(real_tid)
                # Recalculate auto max when tab text changes
                if self._auto_max_tabs:
                    self._recalculate_auto_max_tabs()
                # Remove 'text' from opts_to_set so we don't set it directly on notebook
                del opts_to_set["text"]
            
            # Apply remaining options to underlying notebook
            if opts_to_set:
                result = self.notebook.tab(real_tid, **opts_to_set)

            # Refresh our visible label using lock state + name + status
            self._apply_tab_label(real_tid)
            return ""

        # No options at all: query all options (return base_name for 'text')
        result = self.notebook.tab(real_tid)
        cfg = self._tab_configs.get(real_tid, {})
        result['text'] = cfg.get("name", "")
        return result

    def index(self, tab_id=None):
        """Match ttk.Notebook.index(tab_id)."""
        if tab_id is not None:
            real_tid = self._normalize_tab_id(tab_id)
            if real_tid is None:
                raise tk.TclError("invalid tab id")
            return self.notebook.index(real_tid)

        sel = self.notebook.select()
        if sel is None or self._is_special(sel):
            if self._user_tabs:
                return self.notebook.index(self._user_tabs[0])
            raise tk.TclError("no current tab")
        return self.notebook.index(sel)

    def select(self, element=None):
        if element is not None and element in (self._left_arrow_id, self._right_arrow_id):
            direction = 1 if element == self._right_arrow_id else -1
            self._on_arrow_click(direction)
            return self._last_user_tab

        if element is not None and element == self._config_tab_id:
            self.notebook.select(self._config_tab_id)
            self._refresh_config_items()
            return self._last_user_tab

        if element is not None:
            real_tid = self._normalize_tab_id(element)
            if real_tid is None:
                try:
                    self.notebook.select(element)
                except tk.TclError:
                    pass
                current = self.notebook.select()
                if current and self._is_special(current) and self._user_tabs:
                    self.notebook.select(self._user_tabs[0])
                    self._last_user_tab = self._user_tabs[0]
                elif current and current in self._user_tabs:
                    self._last_user_tab = current
                return self._last_user_tab

            if real_tid in self._user_tabs:
                if not self._is_locked(real_tid):
                    unlocked = self._unlocked_tabs()
                    try:
                        idx_u = unlocked.index(real_tid)
                    except ValueError:
                        idx_u = -1
                    start = self._unlock_scroll
                    locked_count = self._locked_count()
                    room = max(self._max_tabs_visible - locked_count, 0)
                    end = min(start + room, len(unlocked))

                    if 0 <= idx_u < len(unlocked) and (idx_u < start or idx_u >= end):
                        if idx_u < start:
                            self._unlock_scroll = idx_u
                        else:
                            max_start = max(len(unlocked) - room, 0)
                            candidate = idx_u - room + 1
                            self._unlock_scroll = max(0, min(candidate, max_start))
                        self._apply_visibility_window("Select")

            try:
                self.notebook.select(real_tid)
            except tk.TclError:
                pass
            self._last_user_tab = real_tid
            return self._last_user_tab
        else:
            result = self.notebook.select()
            if result and self._is_special(result):
                if self._user_tabs:
                    self.notebook.select(self._user_tabs[0])
                    self._last_user_tab = self._user_tabs[0]
                    return self._last_user_tab
                return None
            if result and result in self._user_tabs:
                self._last_user_tab = result
            return self._last_user_tab