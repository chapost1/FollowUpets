from common.structs import AudioRecord
from gui import ApplicationGUI
from gps_sensor import new_gps_sensor, GPSSensor
from audio import AudioDeviceController
from dal.audio import AudioRecordRepository
from network_interface import NetworkInterface
from common.environment import APPLICATION_GPS_SENSOR_CONFIG, COLLAR_ID


def bind_newtork_interface_to_gui_events(
    gui: ApplicationGUI, network_interface: NetworkInterface
):
    # bind gui events to network interface (to display received data)
    network_interface.on_new_gps_location = gui.update_pet_gps_location
    # bind network interface events to gui (to send data)
    gui.on_send_audio_record_callback = (
        lambda record: network_interface.on_send_voice_message(
            voice_message=record.audio_data
        )
    )


def bind_dal_to_gui_events(
    gui: ApplicationGUI,
    audio_controller: AudioDeviceController,
    audio_record_repository: AudioRecordRepository,
):
    # bind gui events to dal (to manipulate data)
    gui.on_save_audio_record_callback = lambda: audio_record_repository.store_record(
        record=AudioRecord(audio_data=audio_controller.get_audio())
    )
    gui.on_delete_audio_record_callback = audio_record_repository.delete_record
    gui.on_update_audio_record_name_callback = (
        audio_record_repository.update_record_name
    )
    # bind dal events to gui (to display data)
    gui.on_fetch_audio_records_callback = audio_record_repository.get_records


def bind_audio_controller_to_gui_events(
    gui: ApplicationGUI, audio_controller: AudioDeviceController
):
    # bind audio controller to gui (to start/stop recording)
    gui.on_start_recording_callback = audio_controller.start_recording
    gui.on_stop_recording_callback = audio_controller.stop_recording
    gui.on_play_audio_record_callback = lambda record: audio_controller.play_audio(
        audio_data=record.audio_data
    )


def bind_gui_to_user_gps_sensor(gui: ApplicationGUI, user_gps_sensor: GPSSensor):
    # bind gui to user gps sensor (to display current location)
    user_gps_sensor.on_new_location = gui.update_user_gps_location


def main():
    gui = ApplicationGUI()

    user_gps_sensor = new_gps_sensor(**APPLICATION_GPS_SENSOR_CONFIG)
    network_interface = NetworkInterface(collar_id=COLLAR_ID)
    audio_record_repository = AudioRecordRepository()
    audio_controller = AudioDeviceController()

    bind_newtork_interface_to_gui_events(gui=gui, network_interface=network_interface)

    bind_dal_to_gui_events(
        gui=gui,
        audio_controller=audio_controller,
        audio_record_repository=audio_record_repository,
    )

    bind_audio_controller_to_gui_events(gui=gui, audio_controller=audio_controller)

    bind_gui_to_user_gps_sensor(gui=gui, user_gps_sensor=user_gps_sensor)

    user_gps_sensor.start()

    network_interface.start()

    gui.run()

    network_interface.stop()

    user_gps_sensor.stop()


if __name__ == "__main__":
    main()
