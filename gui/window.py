import dearpygui.dearpygui as dpg
from ._node import add_link, remove_link, preview_node
from .node import builder

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

    def viewport_resize_callback(sender, app_data, user_data) -> None:
        dpg.set_item_width('video_editor', app_data[0])
        dpg.set_item_height('video_editor', app_data[1])

    with dpg.window(label='Video Editor', tag='video_editor', width=WIDTH, height=HEIGHT):
        with dpg.menu_bar(label='Video Editor Menu Bar'):
            builder.build('node_editor')

        with dpg.node_editor(label='Node Editor', tag='node_editor',
                             callback=link_callback, delink_callback=delink_callback):
            pass

    dpg.setup_dearpygui()
    dpg.set_viewport_resize_callback(viewport_resize_callback)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()