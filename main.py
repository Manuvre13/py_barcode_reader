from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.logger import Logger
from kivy.utils import platform

import cv2
import numpy as np
from pyzbar import pyzbar
import threading
import time
from datetime import datetime

# Request camera permissions on Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])

class BarcodeReaderApp(App):
    def build(self):
        self.title = "Mobile Barcode Reader"
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Mobile Barcode Reader',
            size_hint_y=None,
            height='48dp',
            font_size='20sp',
            bold=True,
            color=(0, 0.7, 1, 1)
        )
        main_layout.add_widget(title)
        
        # Camera widget
        self.camera = Camera(
            play=False,
            resolution=(640, 480),
            size_hint_y=0.6
        )
        main_layout.add_widget(self.camera)
        
        # Control buttons layout
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            spacing=10
        )
        
        # Start/Stop camera button
        self.camera_btn = Button(
            text='Start Camera',
            background_color=(0, 0.8, 0, 1),
            font_size='16sp'
        )
        self.camera_btn.bind(on_press=self.toggle_camera)
        button_layout.add_widget(self.camera_btn)
        
        # Clear results button
        clear_btn = Button(
            text='Clear Results',
            background_color=(0.8, 0.4, 0, 1),
            font_size='16sp'
        )
        clear_btn.bind(on_press=self.clear_results)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # Status label
        self.status_label = Label(
            text='Ready to scan',
            size_hint_y=None,
            height='30dp',
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # Results section
        results_label = Label(
            text='Scan Results:',
            size_hint_y=None,
            height='30dp',
            font_size='16sp',
            bold=True,
            halign='left'
        )
        results_label.bind(size=results_label.setter('text_size'))
        main_layout.add_widget(results_label)
        
        # Scrollable results area
        scroll = ScrollView(size_hint_y=0.3)
        self.results_text = TextInput(
            text='',
            multiline=True,
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(1, 1, 1, 1),
            font_size='12sp'
        )
        scroll.add_widget(self.results_text)
        main_layout.add_widget(scroll)
        
        # Initialize variables
        self.is_scanning = False
        self.scan_thread = None
        self.last_scan_time = 0
        self.scan_cooldown = 2  # Seconds between duplicate scans
        self.scanned_codes = set()
        
        return main_layout
    
    def toggle_camera(self, instance):
        """Toggle camera on/off"""
        if not self.is_scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        """Start barcode scanning"""
        try:
            self.camera.play = True
            self.is_scanning = True
            self.camera_btn.text = 'Stop Camera'
            self.camera_btn.background_color = (0.8, 0, 0, 1)
            self.status_label.text = 'Camera active - Point at barcode'
            
            # Start scanning in background thread
            self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
            self.scan_thread.start()
            
        except Exception as e:
            self.show_error(f"Failed to start camera: {str(e)}")
    
    def stop_scanning(self):
        """Stop barcode scanning"""
        self.is_scanning = False
        self.camera.play = False
        self.camera_btn.text = 'Start Camera'
        self.camera_btn.background_color = (0, 0.8, 0, 1)
        self.status_label.text = 'Camera stopped'
    
    def scan_loop(self):
        """Main scanning loop"""
        while self.is_scanning:
            try:
                if self.camera.texture:
                    # Get camera frame
                    texture = self.camera.texture
                    if texture is None:
                        time.sleep(0.1)
                        continue
                    
                    # Convert texture to numpy array
                    frame = self.texture_to_array(texture)
                    if frame is not None:
                        self.process_frame(frame)
                
                time.sleep(0.1)  # 10 FPS to save battery
                
            except Exception as e:
                Logger.error(f"Scan loop error: {str(e)}")
                time.sleep(0.5)
    
    def texture_to_array(self, texture):
        """Convert Kivy texture to OpenCV array"""
        try:
            # Get texture data
            buf = texture.pixels
            if not buf:
                return None
            
            # Convert to numpy array
            arr = np.frombuffer(buf, dtype=np.uint8)
            arr = arr.reshape(texture.height, texture.width, 4)  # RGBA
            
            # Convert RGBA to BGR for OpenCV
            arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            
            # Flip vertically (Kivy texture is upside down)
            arr = cv2.flip(arr, 0)
            
            return arr
            
        except Exception as e:
            Logger.error(f"Texture conversion error: {str(e)}")
            return None
    
    def process_frame(self, frame):
        """Process frame for barcodes"""
        try:
            # Decode barcodes
            barcodes = pyzbar.decode(frame)
            
            current_time = time.time()
            
            for barcode in barcodes:
                # Extract barcode data
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                
                # Create unique identifier for this barcode
                barcode_id = f"{barcode_type}:{barcode_data}"
                
                # Check cooldown and duplicates
                if (barcode_id not in self.scanned_codes or 
                    current_time - self.last_scan_time > self.scan_cooldown):
                    
                    self.scanned_codes.add(barcode_id)
                    self.last_scan_time = current_time
                    
                    # Schedule UI update on main thread
                    Clock.schedule_once(
                        lambda dt, bt=barcode_type, bd=barcode_data: 
                        self.add_scan_result(bt, bd)
                    )
                    
                    # Provide haptic feedback on Android
                    if platform == 'android':
                        try:
                            from jnius import autoclass
                            PythonActivity = autoclass('org.kivy.android.PythonActivity')
                            activity = PythonActivity.mActivity
                            context = activity.getApplicationContext()
                            vibrator = context.getSystemService(context.VIBRATOR_SERVICE)
                            vibrator.vibrate(200)  # 200ms vibration
                        except:
                            pass  # Vibration not available
        
        except Exception as e:
            Logger.error(f"Frame processing error: {str(e)}")
    
    def add_scan_result(self, barcode_type, barcode_data):
        """Add scan result to the results display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {barcode_type}\n{barcode_data}\n" + "-"*30 + "\n"
        
        # Add to beginning of results
        current_text = self.results_text.text
        self.results_text.text = result + current_text
        
        # Update status
        self.status_label.text = f'Scanned: {barcode_type}'
        
        # Limit results to prevent memory issues
        lines = self.results_text.text.split('\n')
        if len(lines) > 200:
            self.results_text.text = '\n'.join(lines[:200])
    
    def clear_results(self, instance):
        """Clear scan results"""
        self.results_text.text = ''
        self.scanned_codes.clear()
        self.status_label.text = 'Results cleared'
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def on_pause(self):
        """Handle app pause (Android)"""
        if self.is_scanning:
            self.stop_scanning()
        return True
    
    def on_resume(self):
        """Handle app resume (Android)"""
        pass

# Main app class
class MobileBarcodeReader(BarcodeReaderApp):
    pass

if __name__ == '__main__':
    MobileBarcodeReader().run()