#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import cairo
import subprocess
import threading
import os
import time
import sys
import shutil
from datetime import datetime

# Define CSS for styling
CSS = b"""
.exit-button {
    background-color: #ff5555;
    color: white;
    border-radius: 50%;
    padding: 0px;
    font-weight: bold;
}
.exit-button:hover {
    background-color: #ff0000;
}
.countdown-label {
    color: white;
    background-color: rgba(0, 0, 0, 0.6);
    border-radius: 50%;
    padding: 20px;
    margin: 20px;
}
.transparent-window {
    background-color: rgba(0, 0, 0, 0.1);
}
.countdown-window {
    background-color: rgba(0, 0, 0, 0.7);
}
.recording-button {
    background-color: #ff5555;
    color: white;
    font-weight: bold;
}
.pause-button {
    background-color: #ffaa55;
    color: white;
    font-weight: bold;
}
.resume-button {
    background-color: #55aa55;
    color: white;
    font-weight: bold;
}
.preview-button {
    background-color: #5555ff;
    color: white;
    font-weight: bold;
}
"""

# Countdown window for recording
class CountdownWindow(Gtk.Window):
    def __init__(self, callback, count=2):
        Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        
        # Make the window transparent
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        
        # Make sure we cover the entire screen
        screen = Gdk.Screen.get_default()
        display = screen.get_display()
        monitor = display.get_monitor(0)  # Primary monitor
        geometry = monitor.get_geometry()
        self.set_default_size(geometry.width, geometry.height)
        self.move(0, 0)  # Position at top-left corner
        self.fullscreen()
        
        # Apply CSS for transparency
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            .countdown-container { background-color: rgba(0, 0, 0, 0.3); }
            .countdown-label { font-size: 50px; color: white; }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Connect draw signal
        self.connect("draw", self.on_draw)
        
        # Center the label
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        self.add(box)
        
        # Create a container for the countdown with a semi-transparent background
        countdown_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        countdown_container.set_size_request(150, 150)
        countdown_container.get_style_context().add_class("countdown-container")
        box.pack_start(countdown_container, True, True, 0)
        
        self.label = Gtk.Label()
        self.label.get_style_context().add_class("countdown-label")
        self.label.set_markup(f"<span font='50' color='white'>{count}</span>")
        countdown_container.pack_start(self.label, True, True, 0)
        
        self.count = count
        self.callback = callback
        GLib.timeout_add(1000, self.update_countdown)
    
    def on_draw(self, widget, cr):
        """Draw a semi-transparent overlay."""
        # Get window dimensions
        width, height = self.get_size()
        
        # Fill the entire area with a very light semi-transparent black
        cr.set_source_rgba(0, 0, 0, 0.2)  # 20% opacity - light overlay
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        return False
    
    def update_countdown(self):
        self.count -= 1
        if self.count > 0:
            self.label.set_markup(f"<span font='50' color='white'>{self.count}</span>")
            return True  # Continue the timer
        else:
            self.hide()
            self.callback()
            return False  # Stop the timer

# Area selection window
class AreaSelector(Gtk.Window):
    def __init__(self, parent, is_recording=False):
        Gtk.Window.__init__(self, type=Gtk.WindowType.POPUP)
        self.parent = parent
        self.is_recording = is_recording
        
        # Set window properties
        self.set_decorated(False)
        # Make the window fully transparent initially
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        
        # Make sure we cover the entire screen
        screen = Gdk.Screen.get_default()
        display = screen.get_display()
        monitor = display.get_monitor(0)  # Primary monitor
        geometry = monitor.get_geometry()
        
        # Use get_width/height from geometry instead of deprecated methods
        self.set_default_size(geometry.width, geometry.height)
        self.move(0, 0)  # Position at top-left corner
        self.fullscreen()
        
        # Add events for mouse interaction
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | 
                        Gdk.EventMask.BUTTON_RELEASE_MASK | 
                        Gdk.EventMask.POINTER_MOTION_MASK)
        
        # Connect signals
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_motion)
        self.connect("key-press-event", self.on_key_press)
        self.connect("draw", self.on_draw)  # Connect draw directly to the window
        
        # Selection coordinates
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.is_selecting = False
        self.first_click_done = False  # Track if first click has been made for two-click mode
        self.selection_mode = "drag"   # Default to drag mode, can be "two-click" for two-click selection
        
        # Instructions label with a dark background box
        instructions = "Click and drag to select an area for "
        instructions += "recording" if is_recording else "screenshot"
        instructions += ". Press Escape to cancel."
        
        # Create a box with a dark background for the instructions
        instruction_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        instruction_box.set_halign(Gtk.Align.CENTER)
        instruction_box.set_valign(Gtk.Align.START)
        instruction_box.set_margin_top(20)
        
        # Use CSS styling instead of deprecated override_background_color
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b".dark-bg { background-color: rgba(0, 0, 0, 0.5); }")
        instruction_box.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        instruction_box.get_style_context().add_class("dark-bg")
        
        self.label = Gtk.Label()
        # Fix markup by not using background attribute in span
        self.label.set_markup(f"<span font='14' color='white'><b>{instructions}</b></span>")
        self.label.set_margin_top(10)
        self.label.set_margin_bottom(10)
        self.label.set_margin_start(20)
        self.label.set_margin_end(20)
        instruction_box.add(self.label)
        
        # Add the instruction box to the window
        fixed = Gtk.Fixed()
        self.add(fixed)
        fixed.put(instruction_box, geometry.width // 2 - 200, 20)  # Position at the top center
    
    def on_button_press(self, widget, event):
        """Handle mouse button press to start selection."""
        if self.selection_mode == "drag" or not self.first_click_done:
            # First click in either mode
            self.is_selecting = True
            self.start_x = event.x
            self.start_y = event.y
            self.current_x = event.x
            self.current_y = event.y
            self.first_click_done = True
            
            # Update instructions if in two-click mode
            if self.selection_mode == "two-click":
                instructions = "Click again to complete the selection. Press Escape to cancel."
                self.label.set_markup(f"<span font='14' color='white'><b>{instructions}</b></span>")
        elif self.selection_mode == "two-click" and self.first_click_done:
            # Second click in two-click mode
            self.current_x = event.x
            self.current_y = event.y
            self.finalize_selection()
        
        return True
    
    def on_motion(self, widget, event):
        """Handle mouse motion to update selection rectangle."""
        if self.is_selecting and self.selection_mode == "drag":
            self.current_x = event.x
            self.current_y = event.y
            self.queue_draw()
        elif self.first_click_done and self.selection_mode == "two-click":
            # Update the preview rectangle in two-click mode
            self.current_x = event.x
            self.current_y = event.y
            self.queue_draw()
        return True
    
    def on_button_release(self, widget, event):
        """Handle mouse button release to finalize selection."""
        if self.selection_mode == "drag" and self.is_selecting:
            self.is_selecting = False
            self.current_x = event.x
            self.current_y = event.y
            self.finalize_selection()
        
        return True
    
    def finalize_selection(self):
        """Process the selection and start recording or take screenshot."""
        # Calculate selection rectangle
        x = min(self.start_x, self.current_x)
        y = min(self.start_y, self.current_y)
        width = abs(self.current_x - self.start_x)
        height = abs(self.current_y - self.start_y)
        
        # Ensure minimum size
        if width < 10 or height < 10:
            # Selection too small, ignore
            return
        
        self.hide()
        
        # Process the selection
        if self.is_recording:
            self.parent.start_recording(int(x), int(y), int(width), int(height))
        else:
            self.parent.take_screenshot(int(x), int(y), int(width), int(height))
    
    def on_draw(self, widget, cr):
        """Draw the selection rectangle."""
        # Get window dimensions
        width, height = self.get_size()
        
        # Fill the entire area with a very light semi-transparent black
        # Using an extremely light overlay to ensure screen content is visible
        cr.set_source_rgba(0, 0, 0, 0.05)  # 5% opacity - barely visible
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        if self.is_selecting:
            # Calculate selection rectangle
            x = min(self.start_x, self.current_x)
            y = min(self.start_y, self.current_y)
            rect_width = abs(self.current_x - self.start_x)
            rect_height = abs(self.current_y - self.start_y)
            
            # Draw a slightly darker overlay outside the selection
            cr.set_source_rgba(0, 0, 0, 0.2)
            
            # Draw the four regions outside the selection rectangle
            # Top
            cr.rectangle(0, 0, width, y)
            cr.fill()
            # Bottom
            cr.rectangle(0, y + rect_height, width, height - (y + rect_height))
            cr.fill()
            # Left
            cr.rectangle(0, y, x, rect_height)
            cr.fill()
            # Right
            cr.rectangle(x + rect_width, y, width - (x + rect_width), rect_height)
            cr.fill()
            
            # Draw a border around the selection
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.set_line_width(2)
            cr.rectangle(x, y, rect_width, rect_height)
            cr.stroke()
            
            # Display selection dimensions
            text = f"{int(rect_width)} × {int(rect_height)}"
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            
            # Position text near the selection
            text_x = x + 5
            text_y = y - 10 if y > 30 else y + rect_height + 20
            
            # Draw text background
            text_extents = cr.text_extents(text)
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(text_x - 5, text_y - text_extents.height, 
                        text_extents.width + 10, text_extents.height + 10)
            cr.fill()
            
            # Draw text
            cr.set_source_rgba(1, 1, 1, 1)
            cr.move_to(text_x, text_y)
            cr.show_text(text)
        
        return False
    
    def on_key_press(self, widget, event):
        """Handle key press events to allow canceling with Escape."""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        if keyname == 'Escape':
            self.hide()
            self.parent.show()
            return True
        return False

# Recorder class to manage the recording process
class Recorder:
    def __init__(self, parent, x, y, width, height):
        self.parent = parent
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.process = None
        self.paused = False
        self.temp_files = []
        self.recording_start_time = None
        self.total_recording_time = 0
        self.timer_running = False
        self.setup_control_window()
        self.start_recording()
    
    def setup_control_window(self):
        """Create the recording control window with buttons."""
        self.control_window = Gtk.Window()
        self.control_window.set_decorated(False)
        self.control_window.set_default_size(300, 60)
        
        # Position below the recording area if possible, otherwise above
        screen_height = Gdk.Screen.get_default().get_height()
        if self.y + self.height + 70 < screen_height:
            # Position below the recording area with increased offset to avoid capture
            self.control_window.move(self.x, self.y + self.height + 30)
        else:
            # Position above the recording area with increased offset
            self.control_window.move(self.x, max(10, self.y - 80))
        
        # Ensure the control window is not within the recording area
        self.control_window.set_keep_above(True)
        
        # Main box for controls
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.set_margin_top(5)
        main_box.set_margin_bottom(5)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.control_window.add(main_box)
        
        # Timer label
        self.timer_label = Gtk.Label()
        self.timer_label.set_markup("<b>00:00</b>")
        main_box.pack_start(self.timer_label, False, False, 0)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(button_box, True, True, 0)
        
        # End button
        self.end_button = Gtk.Button(label="End")
        self.end_button.get_style_context().add_class("recording-button")
        self.end_button.connect("clicked", self.on_end_clicked)
        button_box.pack_start(self.end_button, True, True, 0)
        
        # Pause/Resume button
        self.pause_button = Gtk.Button(label="Pause")
        self.pause_button.get_style_context().add_class("pause-button")
        self.pause_button.connect("clicked", self.on_pause_clicked)
        button_box.pack_start(self.pause_button, True, True, 0)
        
        # Start Over button
        self.start_over_button = Gtk.Button(label="Start Over")
        self.start_over_button.connect("clicked", self.on_start_over_clicked)
        button_box.pack_start(self.start_over_button, True, True, 0)
        
        # Connect key press event
        self.control_window.connect("key-press-event", self.on_key_press)
        
        # Connect destroy event
        self.control_window.connect("destroy", self.on_window_destroy)
        
        self.control_window.show_all()
    
    def start_recording(self):
        """Start the recording process."""
        # Generate a unique temporary filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"temp_segment_{timestamp}.mp4"
        self.temp_files.append(temp_file)
        
        # Get the current display - try to use :1 if :0.0 fails
        display = os.environ.get('DISPLAY', ':1')
        
        # Build the FFmpeg command
        cmd = [
            "ffmpeg",
            "-f", "x11grab",
            "-video_size", f"{self.width}x{self.height}",
            "-i", f"{display}+{self.x},{self.y}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-y", temp_file
        ]
        
        print(f"Starting recording: {' '.join(cmd)}")
        
        try:
            # Start the recording process with stderr pipe to capture errors
            self.process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            
            # Start a thread to monitor for FFmpeg errors
            self.monitor_thread = threading.Thread(target=self.monitor_ffmpeg_errors)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            # Start the timer
            self.recording_start_time = time.time()
            self.timer_running = True
            GLib.timeout_add(1000, self.update_timer)
            
            # Update recording state
            self.is_recording = True
            self.is_paused = False
            
        except Exception as e:
            self.show_error_dialog(f"Failed to start recording: {str(e)}")
            self.stop_recording()
    
    def monitor_ffmpeg_errors(self):
        """Monitor FFmpeg process for errors."""
        if not self.process or not self.process.stderr:
            return
            
        # Read the first few lines of stderr to check for startup errors
        for i in range(10):  # Check first 10 lines
            if not self.process or self.process.poll() is not None:
                break
                
            line = self.process.stderr.readline().decode('utf-8', errors='ignore').strip()
            if line and "Error" in line:
                # Use GLib.idle_add to safely call GUI methods from a thread
                GLib.idle_add(self.show_error_dialog, f"FFmpeg error: {line}")
                GLib.idle_add(self.stop_recording)
                break
                
            time.sleep(0.1)  # Small delay between reads
    
    def update_timer(self):
        """Update the recording timer display."""
        if not self.timer_running:
            return False
        
        if self.recording_start_time:
            current_segment_time = time.time() - self.recording_start_time
            total_time = self.total_recording_time + current_segment_time
            
            # Format as MM:SS
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            self.timer_label.set_markup(f"<b>{minutes:02d}:{seconds:02d}</b>")
        
        # Continue the timer
        GLib.timeout_add(1000, self.update_timer)
        return False
    
    def on_pause_clicked(self, widget):
        """Handle pause/resume button click."""
        if not self.paused:
            # Pause recording
            print("Pausing recording")
            if self.process:
                self.process.terminate()
                self.process.wait()
                self.process = None
            
            # Update timer
            if self.recording_start_time:
                self.total_recording_time += time.time() - self.recording_start_time
                self.recording_start_time = None
            
            # Update button
            self.pause_button.set_label("Resume")
            self.pause_button.get_style_context().remove_class("pause-button")
            self.pause_button.get_style_context().add_class("resume-button")
            self.paused = True
            self.timer_running = False
        else:
            # Resume recording
            print("Resuming recording")
            self.start_recording()
            
            # Update button
            self.pause_button.set_label("Pause")
            self.pause_button.get_style_context().remove_class("resume-button")
            self.pause_button.get_style_context().add_class("pause-button")
            self.paused = False
    
    def on_end_clicked(self, widget):
        """Handle end button click."""
        self.stop_recording()
        self.finalize_recording()
    
    def on_start_over_clicked(self, widget):
        """Handle start over button click."""
        print("Starting over")
        
        # Stop current recording
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        
        # Clean up temp files
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"Removed temporary file: {temp_file}")
                except Exception as e:
                    print(f"Error removing temporary file: {e}")
        
        # Reset state
        self.temp_files = []
        self.total_recording_time = 0
        self.recording_start_time = None
        self.paused = False
        
        # Update button
        self.pause_button.set_label("Pause")
        self.pause_button.get_style_context().remove_class("resume-button")
        self.pause_button.get_style_context().add_class("pause-button")
        
        # Start new recording
        self.start_recording()
    
    def stop_recording(self):
        """Stop the current recording process."""
        print("Stopping recording")
        
        # Stop the timer
        self.timer_running = False
        
        # Terminate the FFmpeg process
        if self.process:
            try:
                # Send SIGTERM to FFmpeg to allow it to finish writing the file
                self.process.terminate()
                
                # Wait for the process to finish with a timeout
                try:
                    self.process.wait(timeout=3)  # Wait up to 3 seconds for clean termination
                    print("FFmpeg process terminated cleanly")
                except subprocess.TimeoutExpired:
                    print("FFmpeg process did not terminate in time, forcing...")
                    self.process.kill()  # Force kill if it doesn't terminate
                    self.process.wait()
                    
                self.process = None
            except Exception as e:
                print(f"Error stopping FFmpeg process: {e}")
        
        # Update timer for final time
        if self.recording_start_time:
            self.total_recording_time += time.time() - self.recording_start_time
            self.recording_start_time = None
    
    def finalize_recording(self):
        """Combine all recording segments and create the final output."""
        # Check if we've already finalized
        if hasattr(self, '_finalized') and self._finalized:
            print("Recording already finalized, skipping")
            return
        
        # Mark as finalized to prevent multiple calls
        self._finalized = True
        
        # Create videos directory if it doesn't exist
        os.makedirs("videos", exist_ok=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"videos/recording_{timestamp}.mp4"
        
        if len(self.temp_files) == 1 and os.path.exists(self.temp_files[0]):
            # If only one segment, just rename it
            try:
                # Check if the temp file has content
                temp_file_size = os.path.getsize(self.temp_files[0])
                if temp_file_size == 0:
                    print(f"Warning: Temporary file is empty (0 bytes): {self.temp_files[0]}")
                    self.show_error_dialog(f"Recording failed: The output file is empty (0 bytes). Please try again.")
                    return
                
                print(f"Temporary file size: {temp_file_size} bytes")
                
                # Rename the temp file to the output file
                os.rename(self.temp_files[0], output_file)
                print(f"Recording saved as {output_file}")
            except Exception as e:
                print(f"Error saving recording: {e}")
                # If rename fails, try to copy instead
                try:
                    shutil.copy2(self.temp_files[0], output_file)
                    os.remove(self.temp_files[0])
                    print(f"Recording copied as {output_file}")
                except Exception as e2:
                    print(f"Error copying recording: {e2}")
                    self.show_error_dialog(f"Failed to save recording: {str(e2)}")
                    return
        elif len(self.temp_files) > 1:
            # If multiple segments, create a file list for FFmpeg
            with open("file_list.txt", "w") as f:
                for temp_file in self.temp_files:
                    if os.path.exists(temp_file):
                        f.write(f"file '{temp_file}'\n")
            
            # Combine segments using FFmpeg
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", "file_list.txt",
                "-c", "copy",
                "-y", output_file
            ]
            
            print(f"Combining segments: {' '.join(cmd)}")
            try:
                subprocess.run(cmd, check=True)
                print(f"Recording saved as {output_file}")
                
                # Clean up temp files
                for temp_file in self.temp_files:
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                            print(f"Removed temporary file: {temp_file}")
                        except Exception as e:
                            print(f"Error removing temporary file {temp_file}: {e}")
                
                # Remove the file list
                if os.path.exists("file_list.txt"):
                    try:
                        os.remove("file_list.txt")
                        print("Removed file list")
                    except Exception as e:
                        print(f"Error removing file list: {e}")
            except Exception as e:
                print(f"Error combining segments: {e}")
                self.show_error_dialog(f"Failed to combine recording segments: {str(e)}")
                return
        else:
            print("No temporary files found to finalize recording")
            self.show_error_dialog("Recording failed: No temporary files were created.")
            return
        
        # Verify the output file exists and has content
        if not os.path.exists(output_file):
            print(f"Error: Output file does not exist: {output_file}")
            self.show_error_dialog("Recording failed: The output file was not created.")
            return
        
        output_file_size = os.path.getsize(output_file)
        if output_file_size == 0:
            print(f"Error: Output file is empty (0 bytes): {output_file}")
            self.show_error_dialog("Recording failed: The output file is empty (0 bytes).")
            return
        
        print(f"Final output file size: {output_file_size} bytes")
        
        # Close the control window
        self.control_window.destroy()
        
        # Show preview window instead of main window
        self.parent.show_preview(output_file, is_video=True)
    
    def on_key_press(self, widget, event):
        """Handle key press events."""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        
        if keyname == 'Escape':
            self.on_end_clicked(None)
            return True
        elif keyname == 'space':
            self.on_pause_clicked(None)
            return True
        
        return False
    
    def on_window_destroy(self, widget):
        """Handle window destroy event."""
        print("Control window destroyed")
        self.stop_recording()
        
        # Show the main window if we're not already showing a preview
        # and if we haven't already finalized the recording
        if not hasattr(self, '_finalized') or not self._finalized:
            print("Recording was not finalized, showing main window")
            GLib.idle_add(self.parent.show)

    def show_error_dialog(self, message):
        """Show an error dialog with the given message."""
        dialog = Gtk.MessageDialog(
            transient_for=self.control_window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Recording Error"
        )
        dialog.format_secondary_text(message)
        
        # Connect to the response signal to handle dialog closure
        def on_dialog_response(dialog, response_id):
            dialog.destroy()
            # Close the control window and show the main window
            self.control_window.destroy()
            # Use idle_add to ensure the main window is shown from the main thread
            GLib.idle_add(self.parent.show)
        
        dialog.connect("response", on_dialog_response)
        dialog.show()
        
        # Don't call on_end_clicked here as it would cause a loop
        # Just stop the recording process
        self.stop_recording()

# Preview window for screenshots and recordings
class PreviewWindow(Gtk.Window):
    def __init__(self, parent, file_path, is_video=False):
        Gtk.Window.__init__(self, title="Preview")
        self.parent = parent
        self.file_path = file_path
        self.is_video = is_video
        
        # Set window properties
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(10)
        
        # Main vertical box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # Header box with file info and close button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(header_box, False, False, 0)
        
        # File info label
        file_name = os.path.basename(file_path)
        info_label = Gtk.Label()
        info_label.set_markup(f"<b>{file_name}</b>")
        header_box.pack_start(info_label, True, True, 0)
        
        # Close button in header
        close_header_button = Gtk.Button(label="✕")
        close_header_button.set_tooltip_text("Close Preview")
        close_header_button.connect("clicked", self.on_close_clicked)
        close_header_button.get_style_context().add_class("exit-button")
        header_box.pack_end(close_header_button, False, False, 0)
        
        # Content area
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)
        main_box.pack_start(content_box, True, True, 0)
        
        if is_video:
            # For videos, show a thumbnail or icon and file info
            video_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            video_box.set_halign(Gtk.Align.CENTER)
            video_box.set_valign(Gtk.Align.CENTER)
            content_box.pack_start(video_box, True, True, 0)
            
            # Video icon
            video_icon = Gtk.Image.new_from_icon_name("video-x-generic", Gtk.IconSize.DIALOG)
            video_icon.set_pixel_size(128)  # Make the icon larger
            video_box.pack_start(video_icon, False, False, 10)
            
            # Video info
            video_info = Gtk.Label()
            video_info.set_markup(f"<span size='large'>Video saved as:</span>\n<span size='large'><b>{file_path}</b></span>")
            video_info.set_justify(Gtk.Justification.CENTER)
            video_box.pack_start(video_info, False, False, 10)
            
            # Play button
            play_button = Gtk.Button()
            play_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            play_icon = Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
            play_button_box.pack_start(play_icon, False, False, 0)
            play_label = Gtk.Label(label="Play Video")
            play_button_box.pack_start(play_label, False, False, 0)
            play_button.add(play_button_box)
            
            play_button.get_style_context().add_class("preview-button")
            play_button.connect("clicked", self.on_play_clicked)
            video_box.pack_start(play_button, False, False, 10)
        else:
            # For screenshots, load and display the image
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
                
                # Scale down if needed to fit window
                max_width, max_height = 780, 500
                width, height = pixbuf.get_width(), pixbuf.get_height()
                
                if width > max_width or height > max_height:
                    scale = min(max_width / width, max_height / height)
                    width, height = int(width * scale), int(height * scale)
                    pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
                
                image = Gtk.Image.new_from_pixbuf(pixbuf)
                content_box.pack_start(image, True, True, 0)
            except Exception as e:
                error_label = Gtk.Label(label=f"Error loading image: {e}")
                content_box.pack_start(error_label, True, True, 0)
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        main_box.pack_start(button_box, False, False, 0)
        
        # Save As button
        save_as_button = Gtk.Button(label="Save As...")
        save_as_button.connect("clicked", self.on_save_as_clicked)
        button_box.pack_start(save_as_button, False, False, 0)
        
        # Open folder button
        open_folder_button = Gtk.Button(label="Open Folder")
        open_folder_button.connect("clicked", self.on_open_folder_clicked)
        button_box.pack_start(open_folder_button, False, False, 0)
        
        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self.on_close_clicked)
        button_box.pack_start(close_button, False, False, 0)
        
        # Connect destroy event
        self.connect("destroy", self.on_destroy)
        
        # Show all widgets
        self.show_all()
    
    def on_save_as_clicked(self, widget):
        """Open a file chooser dialog to save the file to a different location."""
        dialog = Gtk.FileChooserDialog(
            title="Save As",
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        
        # Use add_buttons method instead of deprecated buttons parameter
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT
        )
        
        # Set the current name to the original filename without extension
        original_filename = os.path.basename(self.file_path)
        filename_without_ext = os.path.splitext(original_filename)[0]
        dialog.set_current_name(filename_without_ext)
        
        # Set up file filters based on file type
        if self.is_video:
            filter_mp4 = Gtk.FileFilter()
            filter_mp4.set_name("MP4 files")
            filter_mp4.add_pattern("*.mp4")
            dialog.add_filter(filter_mp4)
            
            # Add GIF filter for videos
            filter_gif = Gtk.FileFilter()
            filter_gif.set_name("GIF Animation")
            filter_gif.add_pattern("*.gif")
            dialog.add_filter(filter_gif)
        else:
            filter_png = Gtk.FileFilter()
            filter_png.set_name("PNG Image")
            filter_png.add_pattern("*.png")
            dialog.add_filter(filter_png)
            
            filter_jpg = Gtk.FileFilter()
            filter_jpg.set_name("JPEG Image")
            filter_jpg.add_pattern("*.jpg")
            filter_jpg.add_pattern("*.jpeg")
            dialog.add_filter(filter_jpg)
        
        # Add an "All files" filter
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        
        # Show the dialog and handle the response
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            new_path = dialog.get_filename()
            print(f"Saving file to: {new_path}")
            
            # Get the base path without any extension
            base_path = os.path.splitext(new_path)[0]
            
            # Ensure the file has the correct extension based on the selected filter
            active_filter = dialog.get_filter()
            if active_filter == filter_gif:
                new_path = f"{base_path}.gif"
                print(f"Using .gif extension: {new_path}")
            elif active_filter == filter_mp4:
                new_path = f"{base_path}.mp4"
                print(f"Using .mp4 extension: {new_path}")
            elif active_filter == filter_png:
                new_path = f"{base_path}.png"
                print(f"Using .png extension: {new_path}")
            elif active_filter == filter_jpg:
                new_path = f"{base_path}.jpg"
                print(f"Using .jpg extension: {new_path}")
            elif not os.path.splitext(new_path)[1]:
                # If no extension and no specific filter, add default extension based on file type
                if self.is_video:
                    new_path = f"{new_path}.mp4"
                    print(f"Added default .mp4 extension: {new_path}")
                else:
                    new_path = f"{new_path}.png"
                    print(f"Added default .png extension: {new_path}")
            
            try:
                # For videos, check if we need to convert to GIF
                if self.is_video and new_path.lower().endswith('.gif'):
                    print(f"Converting video to GIF: {self.file_path} -> {new_path}")
                    
                    # Verify the source file exists and has content
                    if not os.path.exists(self.file_path):
                        error_msg = f"Source file does not exist: {self.file_path}"
                        print(error_msg)
                        raise Exception(error_msg)
                    
                    file_size = os.path.getsize(self.file_path)
                    if file_size == 0:
                        error_msg = f"Source file is empty (0 bytes): {self.file_path}"
                        print(error_msg)
                        raise Exception(error_msg)
                    
                    print(f"Source file verified: {self.file_path} ({file_size} bytes)")
                    
                    # Show a progress dialog
                    progress_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.NONE,
                        text="Converting to GIF..."
                    )
                    progress_dialog.format_secondary_text("This may take a moment depending on the video length.")
                    progress_dialog.show_all()
                    
                    # Process GUI events to show the dialog
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                    
                    try:
                        # Get absolute paths to ensure FFmpeg can find the files
                        source_path = os.path.abspath(self.file_path)
                        target_path = os.path.abspath(new_path)
                        
                        print(f"Using absolute paths: {source_path} -> {target_path}")
                        
                        # Ensure target directory exists
                        target_dir = os.path.dirname(target_path)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir, exist_ok=True)
                            print(f"Created target directory: {target_dir}")
                        
                        # Convert MP4 to GIF using FFmpeg with improved command
                        cmd = [
                            "ffmpeg",
                            "-i", source_path,
                            "-vf", "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                            "-y", target_path
                        ]
                        
                        print(f"Running FFmpeg command: {' '.join(cmd)}")
                        
                        # Run the conversion with full output capture
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        # Close the progress dialog
                        progress_dialog.destroy()
                        
                        if result.returncode != 0:
                            error_msg = f"FFmpeg error (code {result.returncode}):\n{result.stderr}"
                            print(error_msg)
                            raise Exception(error_msg)
                        
                        # Verify the output file was created
                        if not os.path.exists(target_path):
                            error_msg = f"GIF file was not created at: {target_path}"
                            print(error_msg)
                            raise Exception(error_msg)
                        
                        output_size = os.path.getsize(target_path)
                        if output_size == 0:
                            error_msg = f"Created GIF file is empty (0 bytes): {target_path}"
                            print(error_msg)
                            raise Exception(error_msg)
                        
                        print(f"GIF conversion completed successfully: {target_path} ({output_size} bytes)")
                    except Exception as e:
                        progress_dialog.destroy()
                        print(f"GIF conversion error: {str(e)}")
                        raise Exception(f"Failed to convert to GIF: {str(e)}")
                    
                # For screenshots, check if we need to convert to JPEG
                elif not self.is_video and (new_path.lower().endswith('.jpg') or new_path.lower().endswith('.jpeg')):
                    print(f"Converting screenshot to JPEG: {self.file_path} -> {new_path}")
                    # Show a progress dialog
                    progress_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.NONE,
                        text="Converting image format..."
                    )
                    progress_dialog.format_secondary_text("This will only take a moment.")
                    progress_dialog.show_all()
                    
                    # Process GUI events to show the dialog
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                    
                    # Convert PNG to JPEG using ImageMagick
                    cmd = [
                        "convert",
                        self.file_path,
                        "-quality", "85",  # Good quality-size balance
                        new_path
                    ]
                    
                    print(f"Running ImageMagick command: {' '.join(cmd)}")
                    
                    # Run the conversion
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    # Close the progress dialog
                    progress_dialog.destroy()
                    
                    if result.returncode != 0:
                        error_msg = f"ImageMagick error: {result.stderr}"
                        print(error_msg)
                        raise Exception(error_msg)
                    
                    print(f"JPEG conversion completed successfully: {new_path}")
                    
                else:
                    # For MP4 or PNG, just copy the file
                    print(f"Copying file: {self.file_path} -> {new_path}")
                    import shutil
                    shutil.copy2(self.file_path, new_path)
                    print(f"File copied successfully: {new_path}")
                
                # Show a success message
                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="File saved successfully"
                )
                success_dialog.format_secondary_text(f"Saved to: {new_path}")
                success_dialog.run()
                success_dialog.destroy()
            except Exception as e:
                # Show an error message
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error saving file"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
        
        dialog.destroy()
    
    def on_play_clicked(self, widget):
        """Open the video file with the default video player."""
        print(f"Attempting to play video: {self.file_path}")
        
        # Check if the file exists
        if not os.path.exists(self.file_path):
            self.show_error_dialog("Video file not found", 
                                  f"The file {self.file_path} does not exist.")
            return
            
        # Check if the file is empty or very small
        file_size = os.path.getsize(self.file_path)
        if file_size == 0:
            self.show_error_dialog("Invalid video file", 
                                  f"The video file is empty (0 bytes). The recording may have failed.")
            return
        elif file_size < 1000:  # Less than 1KB
            print(f"Warning: Video file is very small ({file_size} bytes)")
            self.show_error_dialog("Suspicious video file", 
                                  f"The video file is suspiciously small ({file_size} bytes). It may not play correctly.")
            # Continue anyway to let the user try
        
        print(f"Video file exists and has size: {file_size} bytes")
        
        try:
            # Try to open with xdg-open first
            print("Attempting to open with xdg-open...")
            process = subprocess.Popen(["xdg-open", self.file_path], stderr=subprocess.PIPE)
            
            try:
                # Wait for a short time to see if xdg-open launches successfully
                _, stderr = process.communicate(timeout=3)  # Increased timeout
                
                if process.returncode != 0:
                    stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                    print(f"xdg-open failed with return code {process.returncode}: {stderr_text}")
                    
                    # If xdg-open fails, try specific video players
                    players = ["vlc", "mpv", "totem", "celluloid"]
                    player_found = False
                    
                    for player in players:
                        try:
                            # Check if the player is installed
                            print(f"Checking for {player}...")
                            which_process = subprocess.run(["which", player], capture_output=True, text=True)
                            if which_process.returncode == 0:
                                # Player found, try to use it
                                print(f"Found {player}, attempting to open video...")
                                subprocess.Popen([player, self.file_path])
                                player_found = True
                                print(f"Opened video with {player}")
                                break
                        except Exception as e:
                            print(f"Error checking for {player}: {str(e)}")
                            continue
                    
                    if not player_found:
                        # No suitable player found, show installation suggestions
                        print("No suitable video player found, showing suggestion dialog")
                        self.show_player_suggestion_dialog()
                else:
                    print("Successfully opened video with xdg-open")
            except subprocess.TimeoutExpired:
                # If timeout expired, xdg-open might still be running (which is fine)
                # This usually means it's launching an application
                print("xdg-open is taking longer than expected, but may still be working")
                # Don't terminate the process, let it continue
        except Exception as e:
            print(f"Error in on_play_clicked: {str(e)}")
            self.show_error_dialog("Error opening video", str(e))
    
    def show_error_dialog(self, title, message):
        """Show an error dialog with the given title and message."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def show_player_suggestion_dialog(self):
        """Show a dialog suggesting video players to install."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="No suitable video player found"
        )
        dialog.format_secondary_text(
            "Please install one of the following video players to view MP4 files:\n\n"
            "• VLC Media Player: sudo apt install vlc\n"
            "• MPV: sudo apt install mpv\n"
            "• Totem (GNOME Videos): sudo apt install totem\n"
            "• Celluloid: sudo apt install celluloid"
        )
        dialog.run()
        dialog.destroy()
    
    def on_open_folder_clicked(self, widget):
        """Open the folder containing the file."""
        folder_path = os.path.dirname(os.path.abspath(self.file_path))
        try:
            subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error opening folder"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def on_close_clicked(self, widget):
        """Close the preview window."""
        self.destroy()
    
    def on_destroy(self, widget):
        """Handle window destroy event."""
        # Ensure the parent window is shown when this window is destroyed
        if self.parent:
            GLib.idle_add(self.parent.show)  # Use idle_add to ensure it's called from the main thread

class MainApplication(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_decorated(False)  # No decorations
        self.set_default_size(200, 50)  # Small size
        self.set_position(Gtk.WindowPosition.CENTER)  # Centered
        
        # Add a close button to the window
        self.connect("key-press-event", self.on_key_press)
        
        # Create the main horizontal box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        self.add(box)

        record_button = Gtk.Button(label="Record")
        record_button.connect("clicked", self.on_record_clicked)
        box.pack_start(record_button, True, True, 0)

        screenshot_button = Gtk.Button(label="Screenshot")
        screenshot_button.connect("clicked", self.on_screenshot_clicked)
        box.pack_start(screenshot_button, True, True, 0)
        
        # Add an exit button
        exit_button = Gtk.Button(label="X")
        exit_button.set_size_request(30, 30)  # Make it smaller
        exit_button.connect("clicked", self.on_exit_clicked)
        exit_button.get_style_context().add_class("exit-button")
        box.pack_start(exit_button, False, False, 0)
        
        # Initialize recording process
        self.recording_process = None
        self.recorder = None

    def on_key_press(self, widget, event):
        """Handle key press events to allow closing the window with Escape."""
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        if keyname == 'Escape':
            Gtk.main_quit()
            return True
        return False

    def on_record_clicked(self, widget):
        """Handle the record button click by showing the area selector."""
        print("Record button clicked")
        self.hide()
        selector = AreaSelector(self, is_recording=True)
        selector.show_all()

    def on_screenshot_clicked(self, widget):
        """Handle the screenshot button click by showing the area selector."""
        print("Screenshot button clicked")
        self.hide()
        selector = AreaSelector(self, is_recording=False)
        selector.show_all()
    
    def start_recording(self, x, y, width, height):
        """Start recording the selected area after countdown."""
        print(f"Starting recording of area: x={x}, y={y}, width={width}, height={height}")
        
        def on_countdown_finished():
            """Callback function when countdown finishes."""
            self.recorder = Recorder(self, x, y, width, height)
        
        # Start countdown
        countdown = CountdownWindow(on_countdown_finished)
        countdown.show_all()
    
    def stop_recording(self):
        """Stop the recording process."""
        if self.recording_process:
            print("Stopping recording")
            self.recording_process.terminate()
            self.recording_process = None
            
            # Hide control window if it exists
            if hasattr(self, 'control_window'):
                self.control_window.hide()
            
            # Show main window
            self.show()
    
    def take_screenshot(self, x, y, width, height):
        """Take a screenshot of the selected area."""
        print(f"Taking screenshot of area: x={x}, y={y}, width={width}, height={height}")
        
        # Create screenshots directory if it doesn't exist
        import os
        os.makedirs("screenshots", exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{timestamp}.png"
        
        # Take screenshot using ImageMagick
        cmd = [
            "import",
            "-window", "root",
            "-crop", f"{width}x{height}+{x}+{y}",
            filename
        ]
        print(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd)
        print(f"Screenshot saved as {filename}")
        
        # Show preview window instead of main window
        self.show_preview(filename, is_video=False)

    def on_exit_clicked(self, widget):
        """Handle the exit button click by closing the application."""
        Gtk.main_quit()

    def show_preview(self, file_path, is_video=False):
        """Show a preview window for the captured screenshot or recording."""
        preview_window = PreviewWindow(self, file_path, is_video)
        preview_window.show_all()

def main():
    # Apply CSS styling
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(CSS)
    context = Gtk.StyleContext()
    screen = Gdk.Screen.get_default()
    context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    app = MainApplication()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main() 