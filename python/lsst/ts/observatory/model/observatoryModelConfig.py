import lsst.pex.config as pexConfig
from lsst.sims.utils import Site
import lsst.sims.utils.version as sims_utils_version

__all__ = ['ObservatoryModelConfig', 'TelescopeModelConfig', 'DomeModelConfig', 'RotatorModelConfig',
           'CameraModelConfig', 'OpticsLoopCorrectionModelConfig',
           'SlewRequirementsModelConfig', 'ParkModelConfig']


class ObservatoryModelConfig(pexConfig.Config):
    """A pex_config configuration class for the entire observatory model.
    """
    efd_columns = pexConfig.ListField(doc="List of data required from EFD",
                                      dtype=str,
                                      default=['observatory_state'])
    efd_delta_time = pexConfig.Field(
        doc="Length (delta time) of history to request from the EFD (seconds)",
        dtype=float,
        default=0)
    target_columns = pexConfig.ListField(doc="Names of the keys required in the "
                                             "scheduler target maps (altitude/azimuth)",
                                         dtype=str,
                                         default=['altitude', 'azimuth'])

    site = pexConfig.ConfigField(doc="Location of the observatory site",
                                 dtype=Site,
                                 default=Site('LSST'))
    # Track version of site
    site_version = sims_utils_version.__version__
    site_sha = sims_utils_version.__fingerprint__

    telescope = pexConfig.ConfigField(doc='Configuration parameters for the telescope model',
                                      dtype=TelescopeModelConfig)
    dome = pexConfig.ConfigField(doc='Configuration parameters for the dome model',
                                 dtype=DomeModelConfig)
    rotator = pexConfig.ConfigField(doc='Configuration parameters for the rotator',
                                    dtype=RotatorModelConfig)
    camera = pexConfig.ConfigField(doc='Configuration parameters for the camera',
                                   dtype=CameraModelConfig)
    optics = pexConfig.ConfigField(doc='Configuration parameters for the optics loop corrections',
                                   dtype=OpticsLoopCorrectionModelConfig)
    slew = pexConfig.ConfigField(doc='Configuration parameters for the slew requirements',
                                 dtype=SlewRequirementsModelConfig)
    park = pexConfig.ConfigField(doc='Configuration parameters for park mode',
                                 dtype=ParkModelConfig)


class TelescopeModelConfig(pexConfig.Config):
    """A pex_config configuration class for the telescope parameters.
    """
    altitude_minpos = pexConfig.Field(doc="Minimum altitude from the horizon for the telescope (deg)",
                                      dtype=float,
                                      default=20.0)
    altitude_maxpos = pexConfig.Field(doc="Maximum altitude for the telescope (deg) for zenith avoidance",
                                      dtype=float,
                                      default=86.5)
    azimuth_minpos = pexConfig.Field(doc="Minimum position limit for the azimuth (deg) due to cable wrap",
                                     dtype=float,
                                     default=-270.0)
    azimuth_maxpos = pexConfig.Field(doc="Maximum position limit for the azimuth (deg) due to cable wrap",
                                     dtype=float,
                                     default=270.0)

    altitude_maxspeed = pexConfig.Field(doc="Telescope maximum speed (deg/sec) for the altitude",
                                        dtype=float,
                                        default=3.5)
    altitude_accel = pexConfig.Field(doc="Telescope acceleration rate in altitude (deg/sec/sec)",
                                     dtype=float,
                                     default=3.5)
    altitude_decel = pexConfig.Field(doc="Telescope deceleration rate in altitude (deg/sec/sec)",
                                     dtype=float,
                                     default=3.5)

    azimuth_maxspeed = pexConfig.Field(doc="Telescope maximum speed (deg/sec) for the azimuth",
                                        dtype=float,
                                        default=7.0)
    azimuth_accel = pexConfig.Field(doc="Telescope acceleration rate in azimuth (deg/sec/sec)",
                                    dtype=float,
                                    default=7.0)
    azimuth_decel = pexConfig.Field(doc="Telescope deceleration rate in azimuth (deg/sec/sec)",
                                    dtype=float,
                                    default=7.0)

    settle_time = pexConfig.Field(doc="Telescope settle time (seconds)",
                                  dtype=float,
                                  default=3.0)


class DomeModelConfig(pexConfig.Config):
    """A pex_config configuration class for the telescope parameters.
    """
    altitude_maxspeed = pexConfig.Field(doc="Dome maximum speed (deg/sec) for the altitude",
                                        dtype=float,
                                        default=1.75)
    altitude_accel = pexConfig.Field(doc="Dome acceleration rate in altitude (deg/sec/sec)",
                                     dtype=float,
                                     default=0.875)
    altitude_decel = pexConfig.Field(doc="Dome deceleration rate in altitude (deg/sec/sec)",
                                     dtype=float,
                                     default=0.875)
    altitude_freerange = pexConfig.Field(doc="Dome free range in altitude (deg)",
                                         dtype=float,
                                         default = 0)

    azimuth_maxspeed = pexConfig.Field(doc="Dome maximum speed (deg/sec) for the azimuth",
                                       dtype=float,
                                       default=1.5)
    azimuth_accel = pexConfig.Field(doc="Dome acceleration rate in azimuth (deg/sec/sec)",
                                    dtype=float,
                                    default=0.75)
    azimuth_decel = pexConfig.Field(doc="Dome deceleration rate in azimuth (deg/sec/sec)",
                                    dtype=float,
                                    default=0.75)
    azimuth_freerange = pexConfig.Field(doc="Dome free range in azimuth (deg)",
                                        dtype=float,
                                        default=4)

    settle_time = pexConfig.Field(doc="Dome settle time (seconds) - azimuth only",
                                  dtype=float,
                                  default=1.0)


class RotatorModelConfig(pexConfig.Config):
    """A pex_config configuration class for the rotator parameters.
    """
    minpos = pexConfig.Field(doc="Rotator angle minimum position (deg)",
                             dtype=float,
                             default=-90.0)
    maxpos = pexConfig.Field(doc="Rotator angle maximum position (deg)",
                             dtype=float,
                             default=-90.0)
    filter_change_pos = pexConfig.Field(doc="Rotator angle for filter change (deg)",
                                        dtype=float,
                                        default=0.0)

    maxspeed = pexConfig.Field(doc="Rotator maximum speed (deg/sec)",
                               dtype=float,
                               default=3.5)
    accel = pexConfig.Field(doc="Rotator acceleration rate (deg/sec/sec)",
                            dtype=float,
                            default=1.0)
    decel = pexConfig.Field(doc="Rotator deceleration rate (deg/sec/sec)",
                            dtype=float,
                            default=1.0)


class CameraModelConfig(pexConfig.Config):
    """A pex_config configuration class for the camera parameters.
    """
    readout_time = pexConfig.Field(doc="Readout time (sec)",
                                   dtype=float,
                                   default=2.0)
    shutter_time = pexConfig.Field(doc="Shutter crossing time (sec)",
                                   dtype=float,
                                   default=1.0)
    filter_change_time = pexConfig.Field(doc="Time required to change filter (sec)",
                                         dtype=float,
                                         default=120.0)
    filter_max_changes_burst_num = pexConfig.Field(doc="Maximum number of filter changes within burst_time",
                                                   dtype=int,
                                                   default=1)
    filter_max_changes_burst_time = pexConfig.Field(doc="Time for burst_num of filter changes (sec)",
                                                    dtype=float,
                                                    default=0.0 * 60.0)
    filter_max_changes_avg_num = pexConfig.Field(doc="Maximum number of filter changes within avg_time",
                                                 dtype=int,
                                                 default=3000)
    filter_max_changes_avg_time = pexConfig.Field(doc="Time for avg_num of filter changes (sec)",
                                                  dtype=float,
                                                  default=365.25 * 24 * 60 * 60)
    filter_mounted = pexConfig.ListField(doc="Initial state for the mounted filters",
                                         dtype=str,
                                         default=['g', 'r', 'i', 'z', 'y'])
    filters_removable = pexConfig.ListField(doc="List of filters that are removable for initial swapping",
                                            dtype=str,
                                            default=['z', 'y'])
    filters_umounted = pexConfig.ListField(doc="List of filters which are unmounted in initial state",
                                           dtype=str,
                                           default=['u'])


class OpticsLoopCorrectionModelConfig(pexConfig.Config):
    """A pex_config configuration for the optics loop correction parameters."""
    tel_optics_ol_slope = pexConfig.Field(doc="Delay factor for Open Loop optics correction "
                                              "(sec/deg of altitude slew)",
                                          dtype=float,
                                          default=1.0 / 3.5)
    # The delay factors for closed loop optics correction correspond to requirements
    # based on different altitude slew ranges:
    # for altitude slews between tel_optics_cl_alt_limit[i] <= slew < alt_limit[i+1],
    # the corresponding closed loop optics delay is tel_optics_cl_delay[i]
    tel_optics_cl_delay = pexConfig.ListField(doc="Closed loop optics delay (sec), "
                                                  "for the angles in tel_optics_cl_alt_limit",
                                              dtype=float,
                                              default=[0.0, 36.0])
    tel_optics_cl_alt_limit = pexConfig.ListField(doc="Closed loop optics delay altitude limits (deg)",
                                                  dtype=float,
                                                  default=[0, 9.0, 90.0])


class SlewRequirementsModelConfig(pexConfig.Config):
    """A pex_config configuration class to hold the pre-requisites for each slew activity"""
    # Dependencies between the slew activities - for each activity there is a list of prereqs.
    # Readout corresponds to the previous observation, thus does not have prerequisites and is
    # a pre-req for Exposure (?? not true now?)
    prereq_telalt = pexConfig.ListField(doc="Prerequisites for a telescope altitude slew",
                                        dtype=str,
                                        default=[])
    prereq_telaz = pexConfig.ListField(doc="Prerequisites for a telescope azimuth slew",
                                       dtype=str,
                                       default=[])
    prereq_telsettle = pexConfig.ListField(doc="Prerequisites for telescope settle time",
                                           dtype=str,
                                           default=['telalt', 'telaz'])
    prereq_telrot = pexConfig.ListField(doc="Prerequisites for a rotator slew",
                                        dtype=str,
                                        default = [])
    prereq_telopticsopenloop = pexConfig.ListField(doc="Prerequisites for telescope open loop correction",
                                                   dtype=str,
                                                   default=['telalt', 'telaz'])
    prereq_telopticsclosedloop = pexConfig.ListField(doc="Prerequisites for telescope closed loop correction",
                                                     dtype=str,
                                                     default=['domalt', 'domazsettle', 'telsettle',
                                                              'readout', 'telopticsopenloop',
                                                              'filter', 'telrot'])
    prereq_domalt = pexConfig.ListField(doc="Prerequisites for a dome altitude slew",
                                        dtype=str,
                                        default = [])
    prereq_domaz = pexConfig.ListField(doc="Prerequisites for a dome azimuth slew",
                                       dtype=str,
                                       default=[])
    prereq_domazsettle = pexConfig.ListField(doc="Prerequisites for dome azimuth settle time",
                                           dtype=str,
                                           default=['domaz'])
    prereq_filter = pexConfig.ListField(doc="Prerequisites for a filter change",
                                        dtype=str,
                                        default = [])
    prereq_readout = pexConfig.ListField(doc="Prerequisites for a readout",
                                         dtype=str,
                                         default = [])
    prereq_exposures = pexConfig.ListField(doc="Prerequisites for an exposure",
                                           dtype=str,
                                           default = ['telopticsclosedloop'])


class ParkModelConfig(pexConfig.Config):
    """A pex_config configuration class to describe the telescope parked state
    """
    telescope_altitude = pexConfig.Field(doc="Park position for the telescope in altitude (deg)",
                                         dtype=float,
                                         default=86.5)
    telescope_azimuth = pexConfig.Field(doc="Park position for the telescope in azimuth (deg)",
                                        dtype=float,
                                        default=0.0)
    telescope_rotator = pexConfig.Field(doc="Park position for the telescope rotator (deg)",
                                        dtype=float,
                                        default=0.0)
    dome_altitude = pexConfig.Field(doc="Park position for the dome in altitude (deg)",
                                    dtype=float,
                                    default = 90.0)
    dome_azimuth = pexConfig.Field(doc="Park position for the dome in azimuth (deg)",
                                   dtype=float,
                                   default=0.0)
    filter_position = pexConfig.Field(doc="Park position for the filter changer",
                                      dtype=str,
                                      default='r')



