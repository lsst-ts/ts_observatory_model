import math

__all__ = ["ObservatoryModelParameters"]

class ObservatoryModelParameters(object):
    """Class that collects all of the configuration parameters for the
       observatory.

       All angle parameters are stored as radians. Speeds are radians/sec
       and accelerations are radians/sec^2
    """

    def __init__(self):
        """Initialize the class.
        """
        self.telalt_minpos_rad = 0.0
        self.telalt_maxpos_rad = 0.0
        self.telaz_minpos_rad = 0.0
        self.telaz_maxpos_rad = 0.0
        self.telalt_maxspeed_rad = 0.0
        self.telalt_accel_rad = 0.0
        self.telalt_decel_rad = 0.0
        self.telaz_maxspeed_rad = 0.0
        self.telaz_accel_rad = 0.0
        self.telaz_decel_rad = 0.0
        self.mount_settletime = 0.0

        self.telrot_minpos_rad = 0.0
        self.telrot_maxpos_rad = 0.0
        self.telrot_maxspeed_rad = 0.0
        self.telrot_accel_rad = 0.0
        self.telrot_decel_rad = 0.0
        self.telrot_filterchangepos_rad = 0.0
        self.rotator_followsky = False
        self.rotator_resumeangle = False

        self.domalt_maxspeed_rad = 0.0
        self.domalt_accel_rad = 0.0
        self.domalt_decel_rad = 0.0
        self.domaz_maxspeed_rad = 0.0
        self.domaz_accel_rad = 0.0
        self.domaz_decel_rad = 0.0
        self.domaz_settletime = 0.0

        self.optics_ol_slope = 0.0
        self.optics_cl_delay = []
        self.optics_cl_altlimit = []

        self.readouttime = 0.0
        self.shuttertime = 0.0
        self.filter_changetime = 0.0
        self.filter_darktime = "u"
        self.filter_removable_list = []
        self.filter_max_changes_burst_num = 0
        self.filter_max_changes_burst_time = 0.0
        self.filter_max_changes_avg_num = 0
        self.filter_max_changes_avg_time = 0.0
        self.filter_max_changes_avg_interval = 0.0
        self.filter_init_mounted_list = []
        self.filter_init_unmounted_list = []

        self.prerequisites = {}

    def configure_camera(self, confdict):
        """Configure the camera related parameters.

        Parameters
        ----------
        confdict : dict
            The set of camera configuration parameters.
        """
        self.readouttime = confdict["camera"]["readout_time"]
        self.shuttertime = confdict["camera"]["shutter_time"]
        self.filter_changetime = confdict["camera"]["filter_change_time"]
        self.filter_removable_list = confdict["camera"]["filter_removable"]
        self.filter_max_changes_burst_num = confdict["camera"]["filter_max_changes_burst_num"]
        self.filter_max_changes_burst_time = confdict["camera"]["filter_max_changes_burst_time"]
        self.filter_max_changes_avg_num = confdict["camera"]["filter_max_changes_avg_num"]
        self.filter_max_changes_avg_time = confdict["camera"]["filter_max_changes_avg_time"]
        if self.filter_max_changes_avg_num > 0:
            self.filter_max_changes_avg_interval =\
                self.filter_max_changes_avg_time / self.filter_max_changes_avg_num
        else:
            self.filter_max_changes_avg_interval = 0.0
        try:
            # This is probably not available in most config dicts currently.
            self.camera_fov = confdict["camera"]["field_of_view"]
        except KeyError:
            self.camera_fov = math.radians(3.5)

        self.filter_init_mounted_list = list(confdict["camera"]["filter_mounted"])
        self.filter_init_unmounted_list = list(confdict["camera"]["filter_unmounted"])

    def configure_dome(self, confdict):
        """Configure the dome related parameters.

        Angles must be in degrees, speeds in degrees/sec and accelerations in
        degrees/sec^2.

        Parameters
        ----------
        confdict : dict
            The set of dome configuration parameters.
        """
        self.domalt_maxspeed_rad = math.radians(confdict["dome"]["altitude_maxspeed"])
        self.domalt_accel_rad = math.radians(confdict["dome"]["altitude_accel"])
        self.domalt_decel_rad = math.radians(confdict["dome"]["altitude_decel"])
        self.domaz_maxspeed_rad = math.radians(confdict["dome"]["azimuth_maxspeed"])
        self.domaz_accel_rad = math.radians(confdict["dome"]["azimuth_accel"])
        self.domaz_decel_rad = math.radians(confdict["dome"]["azimuth_decel"])
        self.domaz_settletime = confdict["dome"]["settle_time"]

    def configure_optics(self, confdict):
        """Configure the optics related parameters.

        Slope must be in inverse degrees and altitude limits in degrees.

        Parameters
        ----------
        confdict : dict
            The set of optics configuration parameters.
        """
        self.optics_ol_slope = confdict["optics_loop_corr"]["tel_optics_ol_slope"] / math.radians(1)
        self.optics_cl_delay = list(confdict["optics_loop_corr"]["tel_optics_cl_delay"])
        self.optics_cl_altlimit = list(confdict["optics_loop_corr"]["tel_optics_cl_alt_limit"])
        for index, alt in enumerate(self.optics_cl_altlimit):
            self.optics_cl_altlimit[index] = math.radians(self.optics_cl_altlimit[index])

    def configure_rotator(self, confdict):
        """Configure the telescope rotator related parameters.

        Angles must be in degrees, speeds in degrees/sec and accelerations in
        degrees/sec^2.

        Parameters
        ----------
        confdict : dict
            The set of telescope rotator configuration parameters.
        """
        self.telrot_minpos_rad = math.radians(confdict["rotator"]["minpos"])
        self.telrot_maxpos_rad = math.radians(confdict["rotator"]["maxpos"])
        self.telrot_maxspeed_rad = math.radians(confdict["rotator"]["maxspeed"])
        self.telrot_accel_rad = math.radians(confdict["rotator"]["accel"])
        self.telrot_decel_rad = math.radians(confdict["rotator"]["decel"])
        self.telrot_filterchangepos_rad = \
            math.radians(confdict["rotator"]["filter_change_pos"])
        self.rotator_followsky = confdict["rotator"]["follow_sky"]
        self.rotator_resumeangle = confdict["rotator"]["resume_angle"]

    def configure_slew(self, confdict, activities):
        """Configure the slew related parameters.

        Parameters
        ----------
        confdict : dict
            The set of slew configuration parameters.
        activities : list[str]
            The set of slew activities
        """
        for activity in activities:
            key = "prereq_" + activity
            self.prerequisites[activity] = list(confdict["slew"][key])

    def configure_telescope(self, confdict):
        """Configure the telescope related parameters.

        Angles must be in degrees, speeds in degrees/sec and accelerations in
        degrees/sec^2.

        Parameters
        ----------
        confdict : dict
            The set of telescope configuration parameters.
        """
        self.telalt_minpos_rad = math.radians(confdict["telescope"]["altitude_minpos"])
        self.telalt_maxpos_rad = math.radians(confdict["telescope"]["altitude_maxpos"])
        self.telaz_minpos_rad = math.radians(confdict["telescope"]["azimuth_minpos"])
        self.telaz_maxpos_rad = math.radians(confdict["telescope"]["azimuth_maxpos"])
        self.telalt_maxspeed_rad = math.radians(confdict["telescope"]["altitude_maxspeed"])
        self.telalt_accel_rad = math.radians(confdict["telescope"]["altitude_accel"])
        self.telalt_decel_rad = math.radians(confdict["telescope"]["altitude_decel"])
        self.telaz_maxspeed_rad = math.radians(confdict["telescope"]["azimuth_maxspeed"])
        self.telaz_accel_rad = math.radians(confdict["telescope"]["azimuth_accel"])
        self.telaz_decel_rad = math.radians(confdict["telescope"]["azimuth_decel"])
        self.mount_settletime = confdict["telescope"]["settle_time"]
