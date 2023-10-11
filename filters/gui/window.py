import dearpygui.dearpygui as dpg
from ._node import add_link, remove_link, preview_node
from .node import create_video_clip_node, create_noop_filter_node, create_speed_x_filter_node


WIDTH = 800
HEIGHT = 600


def run() -> None:
    dpg.create_context()
    dpg.create_viewport(title='Sugar Video', width=WIDTH, height=HEIGHT)

    def link_callback(sender, app_data, user_data) -> None:
        link_id = dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        add_link(link_id, app_data[0], app_data[1])

    def delink_callback(sender, app_data, user_data) -> None:
        dpg.delete_item(app_data)
        remove_link(app_data)
        
    def create_video_clip_node_callback(sender, app_data, user_data) -> None:
        create_video_clip_node(user_data)
        
    def create_noop_filter_node_callback(sender, app_data, user_data) -> None:
        create_noop_filter_node(user_data)

    def create_speed_x_filter_node_callback(sender, app_data, user_data) -> None:
        create_speed_x_filter_node(user_data)

    def viewport_resize_callback(sender, app_data, user_data) -> None:
        dpg.set_item_width('video_editor', app_data[0])
        dpg.set_item_height('video_editor', app_data[1])
    
    with dpg.window(label='Video Editor', tag='video_editor', width=WIDTH, height=HEIGHT):
        with dpg.menu_bar(label='Video Editor Menu Bar'):
            with dpg.menu(label='Nodes'):
                dpg.add_menu_item(label='Video Clip',
                                  user_data='node_editor', callback=create_video_clip_node_callback)
                with dpg.menu(label='Filters'):
                    dpg.add_menu_item(label='Filter Noop',
                                      user_data='node_editor', callback=create_noop_filter_node_callback)
                    dpg.add_menu_item(label='Filter Speed X',
                                      user_data='node_editor', callback=create_speed_x_filter_node_callback)
        
        with dpg.node_editor(label='Node Editor', tag='node_editor',
                             callback=link_callback, delink_callback=delink_callback):
            pass

    dpg.setup_dearpygui()
    dpg.set_viewport_resize_callback(viewport_resize_callback)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
