def go_actions(self, event=None):
    """Method to start swinging one or more IV curves when the go
        button is pressed
    """

    # Swing the IV curve, possibly looping
    rc = self.swing_loop(loop_mode=self.loop_mode.get() == "On",
                            first_loop=True)
    if rc == RC_SERIAL_EXCEPTION:
        self.reestablish_arduino_comm()

    # Restore button to "unpressed" appearance
    self.go_button.state(["!pressed"])
    #self.panel_id.focus()

def swing_loop(self, loop_mode=False, first_loop=False):
    """Method that invokes the IVS2 object method to swing the IV curve,
        and then displays the generated GIF in the image pane. In
        loop mode it ends by scheduling another call of itself after
        the programmed delay. In that sense it appears to be a
        loop. Unlike an actual loop, however, it is non-blocking.
        This is essential in order for the GUI not to lock up.
    """
     # Capture the start time
    loop_start_time = dt.datetime.now()

    # Swing battery calibration curve if dynamic bias calibration is
    # enabled
   
    # Turn second relay on for battery + PV curve. This is done
    # regardless of whether dynamic bias calibration is enabled.
    if self.ivs2.battery_bias:
        self.ivs2.second_relay_state = IV_Swinger2.SECOND_RELAY_ON

    # Allow copying the .cfg file to the run directory
    self.suppress_cfg_file_copy = False

    # Call the IVS2 method to swing the curve
    """if loop_mode and (not self.loop_save_results or
                        not self.loop_save_graphs):
        self.ivs2.generate_pdf = False"""
    self.config.remove_axes_and_title()
    panel_id_num = self.panel_id.get()
    rc = self.ivs2.swing_curve(loop_mode=loop_mode, panel_id_num = panel_id_num)
    self.config.add_axes_and_title()
    self.config.update_vref()
    self.ivs2.generate_pdf = True

    plot_ref_failed = (self.ivs2.plot_ref and
                        (rc == RC_PV_MODEL_FAILURE or
                        self.ivs2.pv_model.csv_filename is None))
    if rc == RC_SUCCESS or plot_ref_failed:
        # Update the image pane with the new curve GIF
        self.display_img(self.ivs2.current_img)
        self.current_run_displayed = True
        if plot_ref_failed and not loop_mode:
            # Display dialog if Plot Reference checked but a
            # reference curve was not generated. Suppress this in
            # loop mode.
            self.show_pv_model_failure_dialog()
    elif (loop_mode and
            not self.loop_stop_on_err and
            rc in (RC_ZERO_ISC, RC_ZERO_VOC, RC_ISC_TIMEOUT)):
        # If it failed and we're in loop mode with the stop-on-error option
        # disabled and the error is non-fatal, just clean up and continue
        # after displaying the error message on the screen
        self.display_screen_err_msg(rc)
        self.ivs2.clean_up_after_failure(self.ivs2.hdd_output_dir)
    else:
        # Otherwise return without generating graphs if it failed,
        # displaying reason in a dialog
        return show_error_dialog_clean_up_and_return(rc)

    # Schedule another call with "after" if looping
    """if loop_mode:
        elapsed_time = dt.datetime.now() - loop_start_time
        elapsed_ms = int(round(elapsed_time.total_seconds() * 1000))
        delay_ms = self.loop_delay * 1000 - elapsed_ms
        if not self.loop_rate_limit or delay_ms <= 0:
            delay_ms = 1
        thread_id = self.after(int(delay_ms),
                                lambda: self.swing_loop(loop_mode=True,
                                                        first_loop=False))
        # Captured id is used to cancel when stop button is pressed
        self.swing_loop_id = thread_id"""

    # Save the config to capture current max x,y values and Vref
    self.save_config()

    # Clean up files, depending on mode and options
    self.ivs2.clean_up_files(self.ivs2.hdd_output_dir, loop_mode,
                                self.loop_save_results,
                                self.loop_save_graphs)

    return RC_SUCCESS
