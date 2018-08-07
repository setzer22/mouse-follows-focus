#!/usr/bin/env python3

# Script to implement mouse-follows-focus behavior without
# relying on a specific window manager. Parts of the script
# have been taken from the following sources:
#  - https://stackoverflow.com/questions/5262413/does-xlib-have-an-active-window-event
#  - http://science.su/stuff/so/print_frame_geometry_of_all_windows.py
#  - https://stackoverflow.com/questions/12775136/get-window-position-and-size-in-python-with-xlib

# This code is distributed under the MIT License

import Xlib
import Xlib.display
import time

disp = Xlib.display.Display()
root = disp.screen().root

NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')

last_seen = {'xid': None}
def get_active_window():
    window_id = root.get_full_property(NET_ACTIVE_WINDOW,
                                       Xlib.X.AnyPropertyType).value[0]

    focus_changed = (window_id != last_seen['xid'])
    last_seen['xid'] = window_id

    return window_id, focus_changed

def get_window_geometry(root, window_id):
    try:
        window_obj = disp.create_resource_object('window', window_id)
        while(window_obj.query_tree().parent != root):
            window_obj = window_obj.query_tree().parent
        window_geometry = window_obj.get_geometry()._data
    except Xlib.error.XError:
        window_geometry = None

    return window_geometry

def get_mouse_pos(root):
    x = root.query_pointer()._data['win_x']
    y = root.query_pointer()._data['win_y']
    return x, y


if __name__ == '__main__':
    root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
    while True:
        win, changed = get_active_window()
        if changed:

            # Sleep for a sensible amount of time before looking at window geometry. 
            # This helps with scripts that re-dimension the window after creating it
            time.sleep(0.150); # seconds

            mouseX, mouseY = get_mouse_pos(root)
            geo = get_window_geometry(root, win);

            #print(win, get_window_name(win), get_window_geometry(root, win))

            if geo:
                if mouseX >= geo['x'] and mouseX <= geo['x'] + geo['width'] and \
                   mouseY >= geo['y'] and mouseY <= geo['y'] + geo['height']:
                    #print('Mouse is inside newly focused window')
                    None
                else:
                    #print('Mouse is outside newly focused window')
                    midX = geo['x'] + geo['width'] // 2
                    midY = geo['y'] + geo['height'] // 2

                    geo = get_window_geometry(root, win);
                    root.warp_pointer(midX, midY)

        while True:
            event = disp.next_event()
            if (event.type == Xlib.X.PropertyNotify and
                    event.atom == NET_ACTIVE_WINDOW):
                break

