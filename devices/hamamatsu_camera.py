#!/usr/bin/env python
"""
A ctypes based interface to Hamamatsu cameras.
(tested on a sCMOS Flash 4.0).
The documentation is a little confusing to me on this subject..
I used c_int32 when this is explicitly specified, otherwise I use c_int.
Hazen 10/13
George 11/17 - Updated for SDK4 and to allow fixed length acquisition
Updated for Win7/Win10 usage by Fabian Voigt, June 14th, 2018
A wrapper with GUI added by @nvladimus, 03/2020
"""

config = {
    'simulation': False,
    'image_shape': (2048, 2048),  # (Y,X)
    'sensor_shape': (2048, 2048),  # (Y,X)
    'exposure_ms': 20,
    # triggers in block
    'trigger_in': True,
    'trig_in_mode': 'NORMAL',  # 'NORMAL', 'START'
    'trig_in_source': 'EXTERNAL',  # 'INTERNAL', 'EXTERNAL', 'SOFTWARE', 'MASTER_PULSE'
    'trig_in_type': 'SYNCREADOUT',  # 'EDGE', 'LEVEL', 'SYNCREADOUT'
    'trig_in_polarity': 'NEGATIVE', # 'POSITIVE', 'NEGATIVE'
    # next 4 settings matter only if 'trig_in_source': 'MASTER_PULSE'
    'master_pulse_source': 'EXTERNAL', # 'EXTERNAL', 'SOFTWARE'
    'master_pulse_mode': 'CONTINUOUS', # 'CONTINUOUS', 'START', 'BURST'
    'master_pulse_burst_times': 1,
    'master_pulse_interval_s': 0.1,
    # end of trigger_in block
    # triggers out block
    'trigger_out': True,
    'trig_out_kind': 'EXPOSURE',  # 'LOW', 'EXPOSURE', 'PROGRAMMABLE', 'TRIGGER READY', 'HIGH'
    # next 2 settings matter only if 'trig_out_kind': 'PROGRAMMABLE'
    'trig_out_source':  'MASTER_PULSE', # 'READOUT_END', 'VSYNC', 'MASTER_PULSE'.
    'trig_out_duration_s': 0.001,
    'trig_out_polarity': 'POSITIVE'  # 'POSITIVE', 'NEGATIVE'
    # end of trigger_out block
}

import ctypes
import ctypes.util
import numpy

# for debugging
import sys

dcam = ctypes.windll.dcamapi  # get the DLL handle

# import storm_control.sc_library.halExceptions as halExceptions

# Hamamatsu constants.
DCAMCAP_EVENT_FRAMEREADY = int("0x0002", 0)
# DCAM4 API.
DCAMERR_ERROR = 0
DCAMERR_NOERROR = 1

DCAMPROP_ATTR_HASVALUETEXT = int("0x10000000", 0)
DCAMPROP_ATTR_READABLE = int("0x00010000", 0)
DCAMPROP_ATTR_WRITABLE = int("0x00020000", 0)

DCAMPROP_OPTION_NEAREST = int("0x80000000", 0)
DCAMPROP_OPTION_NEXT = int("0x01000000", 0)
DCAMPROP_OPTION_SUPPORT = int("0x00000000", 0)

DCAMPROP_TYPE_MODE = int("0x00000001", 0)
DCAMPROP_TYPE_LONG = int("0x00000002", 0)
DCAMPROP_TYPE_REAL = int("0x00000003", 0)
DCAMPROP_TYPE_MASK = int("0x0000000F", 0)

DCAMCAP_STATUS_ERROR = int("0x00000000", 0)
DCAMCAP_STATUS_BUSY = int("0x00000001", 0)
DCAMCAP_STATUS_READY = int("0x00000002", 0)
DCAMCAP_STATUS_STABLE = int("0x00000003", 0)
DCAMCAP_STATUS_UNSTABLE = int("0x00000004", 0)

DCAMWAIT_CAPEVENT_FRAMEREADY = int("0x0002", 0)
DCAMWAIT_CAPEVENT_STOPPED = int("0x0010", 0)

DCAMWAIT_RECEVENT_MISSED = int("0x00000200", 0)
DCAMWAIT_RECEVENT_STOPPED = int("0x00000400", 0)
DCAMWAIT_TIMEOUT_INFINITE = int("0x80000000", 0)

DCAM_DEFAULT_ARG = 0

DCAM_IDSTR_MODEL = int("0x04000104", 0)

DCAMCAP_TRANSFERKIND_FRAME = 0

DCAMCAP_START_SEQUENCE = -1
DCAMCAP_START_SNAP = 0

DCAMBUF_ATTACHKIND_FRAME = 0

# Hamamatsu structures.

## DCAMAPI_INIT
#
# The dcam initialization structure
#
class DCAMAPI_INIT(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iDeviceCount", ctypes.c_int32),
            ("reserved", ctypes.c_int32),
            ("initoptionbytes", ctypes.c_int32),
            ("initoption", ctypes.POINTER(ctypes.c_int32)),
            ("guid", ctypes.POINTER(ctypes.c_int32))]

## DCAMDEV_OPEN
#
# The dcam open structure
#
class DCAMDEV_OPEN(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("index", ctypes.c_int32),
            ("hdcam", ctypes.c_void_p)]


## DCAMWAIT_OPEN
#
# The dcam wait open structure
#
class DCAMWAIT_OPEN(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("supportevent", ctypes.c_int32),
            ("hwait", ctypes.c_void_p),
            ("hdcam", ctypes.c_void_p)]

## DCAMWAIT_START
#
# The dcam wait start structure
#
class DCAMWAIT_START(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("eventhappened", ctypes.c_int32),
            ("eventmask", ctypes.c_int32),
            ("timeout", ctypes.c_int32)]

## DCAMCAP_TRANSFERINFO
#
# The dcam capture info structure
#
class DCAMCAP_TRANSFERINFO(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iKind", ctypes.c_int32),
            ("nNewestFrameIndex", ctypes.c_int32),
            ("nFrameCount", ctypes.c_int32)]


## DCAMBUF_ATTACH
#
# The dcam buffer attachment structure
#
class DCAMBUF_ATTACH(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iKind", ctypes.c_int32),
            ("buffer", ctypes.POINTER(ctypes.c_void_p)),
            ("buffercount", ctypes.c_int32)]

## DCAMBUF_FRAME
#
# The dcam buffer frame structure
#
class DCAMBUF_FRAME(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iKind", ctypes.c_int32),
            ("option", ctypes.c_int32),
            ("iFrame", ctypes.c_int32),
            ("buf", ctypes.c_void_p),
            ("rowbytes", ctypes.c_int32),
            ("type", ctypes.c_int32),
            ("width", ctypes.c_int32),
            ("height", ctypes.c_int32),
            ("left", ctypes.c_int32),
            ("top", ctypes.c_int32),
            ("timestamp", ctypes.c_int32),
            ("framestamp", ctypes.c_int32),
            ("camerastamp", ctypes.c_int32)]


## DCAMDEV_STRING
#
# The dcam device string structure
#
class DCAMDEV_STRING(ctypes.Structure):
    _fields_ = [("size", ctypes.c_int32),
            ("iString", ctypes.c_int32),
            ("text", ctypes.c_char_p),
            ("textbytes", ctypes.c_int32)]


## DCAMPROP_ATTR
#
# The dcam property attribute structure.
#
class DCAMPROP_ATTR(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("option", ctypes.c_int32),
                ("iReserved1", ctypes.c_int32),
                ("attribute", ctypes.c_int32),
                ("iGroup", ctypes.c_int32),
                ("iUnit", ctypes.c_int32),
                ("attribute2", ctypes.c_int32),
                ("valuemin", ctypes.c_double),
                ("valuemax", ctypes.c_double),
                ("valuestep", ctypes.c_double),
                ("valuedefault", ctypes.c_double),
                ("nMaxChannel", ctypes.c_int32),
                ("iReserved3", ctypes.c_int32),
                ("nMaxView", ctypes.c_int32),
                ("iProp_NumberOfElement", ctypes.c_int32),
                ("iProp_ArrayBase", ctypes.c_int32),
                ("iPropStep_Element", ctypes.c_int32)]

## DCAMPROP_VALUETEXT
#
# The dcam text property structure.
#
class DCAMPROP_VALUETEXT(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_int32),
                ("iProp", ctypes.c_int32),
                ("value", ctypes.c_double),
                ("text", ctypes.c_char_p),
                ("textbytes", ctypes.c_int32)]


def convertPropertyName(p_name):
    """
    "Regularizes" a property name. We are using all lowercase names with
    the spaces replaced by underscores.
    """
    return p_name.lower().replace(" ", "_")


class DCAMException(Exception):
    pass

class HCamData(object):
    """
    Hamamatsu camera data object.
    Initially I tried to use create_string_buffer() to allocate storage for the
    data from the camera but this turned out to be too slow. The software
    kept falling behind the camera and create_string_buffer() seemed to be the
    bottleneck.
    Using numpy makes a lot more sense anyways..
    """
    def __init__(self, size = None, **kwds):
        """
        Create a data object of the appropriate size.
        """
        super().__init__(**kwds)
        self.np_array = numpy.ascontiguousarray(numpy.empty(int(size/2), dtype=numpy.uint16))
        self.size = size

    def __getitem__(self, slice):
        return self.np_array[slice]

    def copyData(self, address):
        """
        Uses the C memmove function to copy data from an address in memory
        into memory allocated for the numpy array of this object.
        """
        ctypes.memmove(self.np_array.ctypes.data, address, self.size)

    def getData(self):
        return self.np_array

    def getDataPtr(self):
        return self.np_array.ctypes.data

class HamamatsuCamera(object):
    """
    Basic camera interface class.
    This version uses the Hamamatsu library to allocate camera buffers.
    Storage for the data from the camera is allocated dynamically and
    copied out of the camera buffers.
    """
    def __init__(self, camera_id = None, **kwds):
        """
        Open the connection to the camera specified by camera_id.
        """
        super().__init__(**kwds)

        self.buffer_index = 0
        self.camera_id = camera_id
        self.debug = False
        self.encoding = 'utf-8'
        self.frame_bytes = 0
        self.frame_x = 0
        self.frame_y = 0
        self.last_frame_number = 0
        self.properties = None
        self.max_backlog = 0
        self.number_image_buffers = 0

        self.acquisition_mode = "run_till_abort"
        self.number_frames = 0


        # Get camera model.
        self.camera_model = self.getModelInfo(camera_id)

        # Open the camera.
        paramopen = DCAMDEV_OPEN(0, self.camera_id, None)
        paramopen.size = ctypes.sizeof(paramopen)
        self.checkStatus(dcam.dcamdev_open(ctypes.byref(paramopen)),
                         "dcamdev_open")
        self.camera_handle = ctypes.c_void_p(paramopen.hdcam)

        # Set up wait handle
        paramwait = DCAMWAIT_OPEN(0, 0, None, self.camera_handle)
        paramwait.size = ctypes.sizeof(paramwait)
        self.checkStatus(dcam.dcamwait_open(ctypes.byref(paramwait)),
                "dcamwait_open")
        self.wait_handle = ctypes.c_void_p(paramwait.hwait)

        # Get camera properties.
        self.properties = self.getCameraProperties()

        # Get camera max width, height.
        # self.max_width = self.getPropertyValue("image_width")[0]
        # self.max_height = self.getPropertyValue("image_height")[0]
        self.max_width = self.getPropertyValue("image_width")
        self.max_height = self.getPropertyValue("image_height")


    def captureSetup(self):
        """
        Capture setup (internal use only). This is called at the start
        of new acquisition sequence to determine the current ROI and
        get the camera configured properly.
        """
        self.buffer_index = -1
        self.last_frame_number = 0

        # Set sub array mode.
        self.setSubArrayMode()

        # Get frame properties.
        self.frame_x = self.getPropertyValue("image_width")[0]
        self.frame_y = self.getPropertyValue("image_height")[0]
        self.frame_bytes = self.getPropertyValue("image_framebytes")[0]


    def checkStatus(self, fn_return, fn_name= "unknown"):
        """
        Check return value of the dcam function call.
        Throw an error if not as expected?
        """
        #if (fn_return != DCAMERR_NOERROR) and (fn_return != DCAMERR_ERROR):
        #    raise DCAMException("dcam error: " + fn_name + " returned " + str(fn_return))
        #if fn_return != DCAMERR_NOERROR:
        if fn_return == DCAMERR_ERROR:
            c_buf_len = 80
            c_buf = ctypes.create_string_buffer(c_buf_len)
            c_error = dcam.dcam_getlasterror(self.camera_handle,
                                             c_buf,
                                             ctypes.c_int32(c_buf_len))
            #print("dcam error " + fn_name + " " + str(c_buf.value))
            raise DCAMException("dcam error " + str(fn_name) + " " + str(c_buf.value))

        return fn_return

    def getCameraProperties(self):
        """
        Return the ids & names of all the properties that the camera supports. This
        is used at initialization to populate the self.properties attribute.
        """
        c_buf_len = 64
        c_buf = ctypes.create_string_buffer(c_buf_len)
        properties = {}
        prop_id = ctypes.c_int32(0)

        # Reset to the start.
        ret = dcam.dcamprop_getnextid(self.camera_handle,
                                      ctypes.byref(prop_id),
                                      ctypes.c_uint32(DCAMPROP_OPTION_NEAREST))
        if (ret != 0) and (ret != DCAMERR_NOERROR):
            self.checkStatus(ret, "dcamprop_getnextid")

        # Get the first property.
        ret = dcam.dcamprop_getnextid(self.camera_handle,
                                          ctypes.byref(prop_id),
                                          ctypes.c_int32(DCAMPROP_OPTION_NEXT))
        if (ret != 0) and (ret != DCAMERR_NOERROR):
            self.checkStatus(ret, "dcamprop_getnextid")
        self.checkStatus(dcam.dcamprop_getname(self.camera_handle,
                                                   prop_id,
                                                   c_buf,
                                                   ctypes.c_int32(c_buf_len)),
                         "dcamprop_getname")

        # Get the rest of the properties.
        last = -1
        while prop_id.value != last:
            last = prop_id.value
            properties[convertPropertyName(c_buf.value.decode(self.encoding))] = prop_id.value
            ret = dcam.dcamprop_getnextid(self.camera_handle,
                                              ctypes.byref(prop_id),
                                              ctypes.c_int32(DCAMPROP_OPTION_NEXT))
            if (ret != 0) and (ret != DCAMERR_NOERROR):
                self.checkStatus(ret, "dcamprop_getnextid")
            self.checkStatus(dcam.dcamprop_getname(self.camera_handle,
                                                       prop_id,
                                                       c_buf,
                                                       ctypes.c_int32(c_buf_len)),
                             "dcamprop_getname")
        return properties

    def getFrames(self):
        """
        Gets all of the available frames.

        This will block waiting for new frames even if
        there new frames available when it is called.
        """
        frames = []
        for n in self.newFrames():
            paramlock = DCAMBUF_FRAME(
                    0, 0, 0, n, None, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            paramlock.size = ctypes.sizeof(paramlock)

            # Lock the frame in the camera buffer & get address.
            self.checkStatus(dcam.dcambuf_lockframe(self.camera_handle,
                                                ctypes.byref(paramlock)),
                             "dcambuf_lockframe")

            # Create storage for the frame & copy into this storage.
            hc_data = HCamData(self.frame_bytes)
            hc_data.copyData(paramlock.buf)
            frames.append(hc_data)

        return [frames, [self.frame_y, self.frame_x]]

    def getModelInfo(self, camera_id):
        """
        Returns the model of the camera
        """

        c_buf_len = 20
        string_value = ctypes.create_string_buffer(c_buf_len)
        paramstring = DCAMDEV_STRING(
                        0,
                        DCAM_IDSTR_MODEL,
                        ctypes.cast(string_value, ctypes.c_char_p),
                        c_buf_len)
        paramstring.size = ctypes.sizeof(paramstring)

        self.checkStatus(dcam.dcamdev_getstring(ctypes.c_int32(camera_id),
                                                ctypes.byref(paramstring)),
                         "dcamdev_getstring")

        return string_value.value.decode(self.encoding)

    def getProperties(self):
        """
        Return the list of camera properties. This is the one to call if you
        want to know the camera properties.
        """
        return self.properties

    def getPropertyAttribute(self, property_name):
        """
        Return the attribute structure of a particular property.

        FIXME (OPTIMIZATION): Keep track of known attributes?
        """
        p_attr = DCAMPROP_ATTR()
        p_attr.cbSize = ctypes.sizeof(p_attr)
        p_attr.iProp = self.properties[property_name]
        ret = self.checkStatus(dcam.dcamprop_getattr(self.camera_handle,
                                                         ctypes.byref(p_attr)),
                               "dcamprop_getattr")
        if ret == 0:
            print("property", property_id, "is not supported")
            return False
        else:
            return p_attr

    def getPropertyRange(self, property_name):
        """
        Return the range for an attribute.
        """
        prop_attr = self.getPropertyAttribute(property_name)
        temp = prop_attr.attribute & DCAMPROP_TYPE_MASK
        if temp == DCAMPROP_TYPE_REAL:
            return [float(prop_attr.valuemin), float(prop_attr.valuemax)]
        else:
            return [int(prop_attr.valuemin), int(prop_attr.valuemax)]

    def getPropertyRW(self, property_name):
        """
        Return if a property is readable / writeable.
        """
        prop_attr = self.getPropertyAttribute(property_name)
        rw = []

        # Check if the property is readable.
        if (prop_attr.attribute & DCAMPROP_ATTR_READABLE):
            rw.append(True)
        else:
            rw.append(False)

        # Check if the property is writeable.
        if (prop_attr.attribute & DCAMPROP_ATTR_WRITABLE):
            rw.append(True)
        else:
            rw.append(False)

        return rw

    def getPropertyText(self, property_name):
        """
        #Return the text options of a property (if any).
        """
        prop_attr = self.getPropertyAttribute(property_name)
        if not (prop_attr.attribute & DCAMPROP_ATTR_HASVALUETEXT):
            return {}
        else:
            # Create property text structure.
            prop_id = self.properties[property_name]
            v = ctypes.c_double(prop_attr.valuemin)

            prop_text = DCAMPROP_VALUETEXT()
            c_buf_len = 64
            c_buf = ctypes.create_string_buffer(c_buf_len)
            #prop_text.text = ctypes.c_char_p(ctypes.addressof(c_buf))
            prop_text.cbSize = ctypes.c_int32(ctypes.sizeof(prop_text))
            prop_text.iProp = ctypes.c_int32(prop_id)
            prop_text.value = v
            prop_text.text = ctypes.addressof(c_buf)
            prop_text.textbytes = c_buf_len

            # Collect text options.
            done = False
            text_options = {}
            while not done:
                # Get text of current value.
                self.checkStatus(dcam.dcamprop_getvaluetext(self.camera_handle,
                                                ctypes.byref(prop_text)),
                                 "dcamprop_getvaluetext")
                text_options[prop_text.text.decode(self.encoding)] = int(v.value)

                # Get next value.
                ret = dcam.dcamprop_queryvalue(self.camera_handle,
                                           ctypes.c_int32(prop_id),
                                           ctypes.byref(v),
                                           ctypes.c_int32(DCAMPROP_OPTION_NEXT))
                prop_text.value = v

                if (ret != 1):
                    done = True

            return text_options

    def getPropertyValue(self, property_name):
        """
        Return the current setting of a particular property.
        """

        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name:", property_name)
            return False
        prop_id = self.properties[property_name]

        # Get the property attributes.
        prop_attr = self.getPropertyAttribute(property_name)

        # Get the property value.
        c_value = ctypes.c_double(0)
        self.checkStatus(dcam.dcamprop_getvalue(self.camera_handle,
                                                    ctypes.c_int32(prop_id),
                                                    ctypes.byref(c_value)),
                         "dcamprop_getvalue")

        # Convert type based on attribute type.
        temp = prop_attr.attribute & DCAMPROP_TYPE_MASK
        if (temp == DCAMPROP_TYPE_MODE):
            prop_type = "MODE"
            prop_value = int(c_value.value)
        elif (temp == DCAMPROP_TYPE_LONG):
            prop_type = "LONG"
            prop_value = int(c_value.value)
        elif (temp == DCAMPROP_TYPE_REAL):
            prop_type = "REAL"
            prop_value = c_value.value
        else:
            prop_type = "NONE"
            prop_value = False

        return [prop_value, prop_type]

    def isCameraProperty(self, property_name):
        """
        Check if a property name is supported by the camera.
        """
        if (property_name in self.properties):
            return True
        else:
            return False

    def newFrames(self):
        """
        Return a list of the ids of all the new frames since the last check.
        Returns an empty list if the camera has already stopped and no frames
        are available.

        This will block waiting for at least one new frame.
        """
        # Wait for a new frame.
        # paramstart = DCAMWAIT_START(
        #         0, 0, DCAMCAP_EVENT_FRAMEREADY, DCAMWAIT_TIMEOUT_INFINITE)
        paramstart = DCAMWAIT_START(
                0, 0, DCAMCAP_EVENT_FRAMEREADY, 1000)

        paramstart.size = ctypes.sizeof(paramstart)

        self.checkStatus(dcam.dcamwait_start(self.wait_handle,
                                        ctypes.byref(paramstart)),
                         "dcamwait_start")
        # Removed and updated from an older version to get around a triggering bug
        # captureStatus = ctypes.c_int32(0)
        # self.checkStatus(dcam.dcamcap_status(
        #     self.camera_handle, ctypes.byref(captureStatus)))
        #
        # # Wait for a new frame if the camera is acquiring.
        # if captureStatus.value == DCAMCAP_STATUS_BUSY:
        #     paramstart = DCAMWAIT_START(
        #             0,
        #             0,
        #             DCAMWAIT_CAPEVENT_FRAMEREADY | DCAMWAIT_CAPEVENT_STOPPED,
        #             100)
        #     paramstart.size = ctypes.sizeof(paramstart)
        #     self.checkStatus(dcam.dcamwait_start(self.wait_handle,
        #                                     ctypes.byref(paramstart)),
        #                      "dcamwait_start")

        # Check how many new frames there are.
        paramtransfer = DCAMCAP_TRANSFERINFO(
                0, DCAMCAP_TRANSFERKIND_FRAME, 0, 0)
        paramtransfer.size = ctypes.sizeof(paramtransfer)
        self.checkStatus(dcam.dcamcap_transferinfo(self.camera_handle,
                                               ctypes.byref(paramtransfer)),
                         "dcamcap_transferinfo")
        cur_buffer_index = paramtransfer.nNewestFrameIndex
        cur_frame_number = paramtransfer.nFrameCount

        # Check that we have not acquired more frames than we can store in our buffer.
        # Keep track of the maximum backlog.
        backlog = cur_frame_number - self.last_frame_number
        if backlog > self.number_image_buffers:
            print(">> Warning! hamamatsu camera frame buffer overrun detected!")
        if (backlog > self.max_backlog):
            self.max_backlog = backlog
        self.last_frame_number = cur_frame_number


        # Create a list of the new frames.
        new_frames = []
        if (cur_buffer_index < self.buffer_index):
            for i in range(self.buffer_index + 1, self.number_image_buffers):
                new_frames.append(i)
            for i in range(cur_buffer_index + 1):
                new_frames.append(i)
        else:
            for i in range(self.buffer_index, cur_buffer_index):
                new_frames.append(i+1)
        self.buffer_index = cur_buffer_index

        if self.debug:
            print(new_frames)

        return new_frames

    def setPropertyValue(self, property_name, property_value):
        """
        Set the value of a property.
        """

        # Check if the property exists.
        if not (property_name in self.properties):
            print(" unknown property name:", property_name)
            return False

        # If the value is text, figure out what the
        # corresponding numerical property value is.
        if (isinstance(property_value, str)):
            text_values = self.getPropertyText(property_name)
            if (property_value in text_values):
                property_value = float(text_values[property_value])
            else:
                print(" unknown property text value:", property_value, "for", property_name)
                return False

        # Check that the property is within range.
        [pv_min, pv_max] = self.getPropertyRange(property_name)
        if property_value < pv_min:
            print(" set property value", property_value, "is less than minimum of", pv_min, property_name, "setting to minimum")
            property_value = pv_min
        if property_value > pv_max:
            print(" set property value", property_value, "is greater than maximum of", pv_max, property_name, "setting to maximum")
            property_value = pv_max

        # Set the property value, return what it was set too.
        prop_id = self.properties[property_name]
        p_value = ctypes.c_double(property_value)
        self.checkStatus(dcam.dcamprop_setgetvalue(self.camera_handle,
                                           ctypes.c_int32(prop_id),
                                           ctypes.byref(p_value),
                                           ctypes.c_int32(DCAM_DEFAULT_ARG)),
                         "dcamprop_setgetvalue")
        return p_value.value

    def setSubArrayMode(self):
        """
        This sets the sub-array mode as appropriate based on the current ROI.
        """

        # Check ROI properties.
        roi_w = self.getPropertyValue("subarray_hsize")[0]
        roi_h = self.getPropertyValue("subarray_vsize")[0]

        # If the ROI is smaller than the entire frame turn on subarray mode
        if (roi_w == self.max_width) and (roi_h == self.max_height):
            self.setPropertyValue("subarray_mode", "OFF")
        else:
            self.setPropertyValue("subarray_mode", "ON")

    def setACQMode(self, mode, number_frames = None):
        '''
        Set the acquisition mode to either run until aborted or to
        stop after acquiring a set number of frames.
        mode should be either "fixed_length" or "run_till_abort"
        if mode is "fixed_length", then number_frames indicates the number
        of frames to acquire.
        '''

        if self.acquisition_mode is "fixed_length" or \
                self.acquisition_mode is "run_till_abort":
            self.acquisition_mode = mode
            self.number_frames = number_frames
        else:
            raise DCAMException("Unrecognized acqusition mode: " + mode)


    def startAcquisition(self):
        """
        Start data acquisition.
        """
        self.captureSetup()
        self.allocateBuffers()

        # Start acquisition.
        if self.acquisition_mode is "run_till_abort":
            self.checkStatus(dcam.dcamcap_start(self.camera_handle,
                                    DCAMCAP_START_SEQUENCE),
                             "dcamcap_start")
        if self.acquisition_mode is "fixed_length":
            self.checkStatus(dcam.dcamcap_start(self.camera_handle,
                                    DCAMCAP_START_SNAP),
                             "dcamcap_start")

    def allocateBuffers(self):
        # Allocate Hamamatsu image buffers.
        # We allocate enough to buffer 10 seconds of data or the specified
        # number of frames for a fixed length acquisition
        #
        if self.acquisition_mode is "run_till_abort":
            n_buffers = int(10 * self.getPropertyValue("internal_frame_rate")[0])
        elif self.acquisition_mode is "fixed_length":
            n_buffers = self.number_frames
        self.number_image_buffers = n_buffers
        self.checkStatus(dcam.dcambuf_alloc(self.camera_handle,
                                            ctypes.c_int32(self.number_image_buffers)),
                         "dcambuf_alloc")

    def stopAcquisition(self):
        """
        Stop data acquisition.
        """
        self.checkStatus(dcam.dcamcap_stop(self.camera_handle),
                         "dcamcap_stop")

        #print("max camera backlog was", self.max_backlog, "of", self.number_image_buffers)
        self.max_backlog = 0

        # Free image buffers.
        self.number_image_buffers = 0
        self.checkStatus(dcam.dcambuf_release(self.camera_handle,
                                              DCAMBUF_ATTACHKIND_FRAME),
                         "dcambuf_release")

    def shutdown(self):
        """
        Close down the connection to the camera.
        """
        self.checkStatus(dcam.dcamwait_close(self.wait_handle), "dcamwait_close")
        self.checkStatus(dcam.dcamdev_close(self.camera_handle), "dcamdev_close")
        self.checkStatus(dcam.dcamapi_uninit(), "dcamapi_uninit")

    def sortedPropertyTextOptions(self, property_name):
        """
        Returns the property text options a list sorted by value.
        """
        text_values = self.getPropertyText(property_name)
        return sorted(text_values, key = text_values.get)


class HamamatsuCameraMR(HamamatsuCamera):
    """
    Memory recycling camera class.

    This version allocates "user memory" for the Hamamatsu camera
    buffers. This memory is also the location of the storage for
    the np_array element of a HCamData() class. The memory is
    allocated once at the beginning, then recycled. This means
    that there is a lot less memory allocation & shuffling compared
    to the basic class, which performs one allocation and (I believe)
    two copies for each frame that is acquired.

    WARNING: There is the potential here for chaos. Since the memory
             is now shared there is the possibility that downstream code
             will try and access the same bit of memory at the same time
             as the camera and this could end badly.
    FIXME: Use lockbits (and unlockbits) to avoid memory clashes?
           This would probably also involve some kind of reference
           counting scheme.
    UPDATE (nvladimus): don't use this class if you pass frames to other threads
    (eg via deque.append), and manipulate the list/deque in those threads (eg. deque.popleft).
    The acquisition freezes as it approaches the end ("fixed_length" mode),
    probably because of buffer access conflict.
    Using locks and unlocks does not help. Use the base class HamamatsuCamera() instead.
    """
    def __init__(self, **kwds):
        super().__init__(**kwds)

        self.hcam_data = []
        self.hcam_ptr = False
        self.old_frame_bytes = -1

        self.setPropertyValue("output_trigger_kind[0]", 2)

    def getFrames(self):
        """
        Gets all of the available frames.

        This will block waiting for new frames even if there new frames
        available when it is called.

        FIXME: It does not always seem to block? The length of frames can
               be zero. Are frames getting dropped? Some sort of race condition?
        """
        frames = []
        for n in self.newFrames():
            frames.append(self.hcam_data[n])

        return [frames, [self.frame_x, self.frame_y]]

    def startAcquisition(self):
        """
        Allocate as many frames as will fit in 2GB of memory and start data acquisition.
        """
        self.captureSetup()

        # Allocate new image buffers if necessary. This will allocate
        # as many frames as can fit in 2GB of memory, or 2000 frames,
        # which ever is smaller. The problem is that if the frame size
        # is small than a lot of buffers can fit in 2GB. Assuming that
        # the camera maximum speed is something like 1KHz 2000 frames
        # should be enough for 2 seconds of storage, which will hopefully
        # be long enough.
        #
        if (self.old_frame_bytes != self.frame_bytes) or \
                (self.acquisition_mode is "fixed_length"):

            n_buffers = min(int((2.0 * 1024 * 1024 * 1024)/self.frame_bytes), 2000)
            if self.acquisition_mode is "fixed_length":
                self.number_image_buffers = self.number_frames
            else:
                self.number_image_buffers = n_buffers

            # Allocate new image buffers.
            ptr_array = ctypes.c_void_p * self.number_image_buffers
            self.hcam_ptr = ptr_array()
            self.hcam_data = []
            for i in range(self.number_image_buffers):
                hc_data = HCamData(self.frame_bytes)
                self.hcam_ptr[i] = hc_data.getDataPtr()
                self.hcam_data.append(hc_data)

            self.old_frame_bytes = self.frame_bytes

        # Attach image buffers and start acquisition.
        #
        # We need to attach & release for each acquisition otherwise
        # we'll get an error if we try to change the ROI in any way
        # between acquisitions.

        paramattach = DCAMBUF_ATTACH(0, DCAMBUF_ATTACHKIND_FRAME,
                self.hcam_ptr, self.number_image_buffers)
        paramattach.size = ctypes.sizeof(paramattach)

        if self.acquisition_mode is "run_till_abort":
            self.checkStatus(dcam.dcambuf_attach(self.camera_handle,
                                    paramattach),
                             "dcam_attachbuffer")
            self.checkStatus(dcam.dcamcap_start(self.camera_handle,
                                    DCAMCAP_START_SEQUENCE),
                             "dcamcap_start")
        if self.acquisition_mode is "fixed_length":
            paramattach.buffercount = self.number_frames
            self.checkStatus(dcam.dcambuf_attach(self.camera_handle,
                                    paramattach),
                             "dcambuf_attach")
            self.checkStatus(dcam.dcamcap_start(self.camera_handle,
                                    DCAMCAP_START_SNAP),
                             "dcamcap_start")


    def stopAcquisition(self):
        """
        Stop data acquisition and release the memory associates with the frames.
        """
        # Stop acquisition.
        self.checkStatus(dcam.dcamcap_stop(self.camera_handle),
                         "dcamcap_stop")
        # Release image buffers.
        if self.hcam_ptr:
            self.checkStatus(dcam.dcambuf_release(self.camera_handle,
                                                DCAMBUF_ATTACHKIND_FRAME),
                         "dcambuf_release")

        ''' Print backlog only when it is large '''
        if self.max_backlog > 1:
            print("max camera backlog was:", self.max_backlog)
        self.max_backlog = 0

##################
## GUI frontend ##
##################

import kekse
import numpy as np
import logging
from functools import partial
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
logging.basicConfig()


class CamController(QtCore.QObject):
    sig_update_gui = pyqtSignal()

    def __init__(self, dev_name='Hamamatsu Orca Flash4.3', gui_on=True, logger_name='Orca'):
        """High-level camera control with optional GUI frontend. By @nvladimus"""
        super().__init__()
        self.dev_handle = None
        self.config = config
        self.exposure_ms = self.config['exposure_ms']
        self.status = 'Not_connected'  # 'Not_connected', 'Connected', 'Idle', 'Running'
        self.abort = False
        self.last_image = None
        self.frame_height_px = self.config['image_shape'][1]
        self.cam_voffset = 0
        self.frame_readout_ms = 10.0
        self.trigger_in = self.config['trigger_in']
        self.trigger_out = self.config['trigger_out']
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        # GUI setup
        self.gui_on = gui_on
        if self.gui_on:
            self.logger.debug("Camera GUI on")
            self.gui = kekse.ProtoKeks(dev_name)
            self._setup_gui()
            self.sig_update_gui.connect(self._update_gui)

    def initialize(self):
        if self.config['simulation']:
            self.logger.debug("Connected to SimulatedCamera")
        else:
            if self.dev_handle is None:
                param_init = DCAMAPI_INIT(0, 0, 0, 0, None, None)
                param_init.size = ctypes.sizeof(param_init)
                error_code = dcam.dcamapi_init(ctypes.byref(param_init))
                if error_code != DCAMERR_NOERROR:
                    self.logger.fatal(f"DCAM initialization failed with error code {error_code}")
                n_cameras = param_init.iDeviceCount
                if n_cameras > 0:
                    self.dev_handle = HamamatsuCamera(camera_id=0)
                    self.logger.info(f"Connected to Camera 0, model {self.dev_handle.getModelInfo(0)}")
                    self.status = 'Connected'
                    self.setup()
                    self.last_image = np.random.randint(75, 125, size=self.config['image_shape'], dtype='uint16')
            else:
                self.logger.error("Camera already initialized!")

    def setup(self):
        if self.config['simulation']:
            pass
        elif self.dev_handle is not None:
            min_exposure_time = self.dev_handle.getPropertyValue("timing_readout_time")[0]
            if min_exposure_time <= self.exposure_ms/1000.:
                self.dev_handle.setPropertyValue("exposure_time", self.exposure_ms/1000.)
                self.dev_handle.setPropertyValue("readout_speed", 2)
                # self.logger.debug(f"Camera exposure time, ms: {self.exposure_ms}")
                self.setup_triggers()
            else:
                self.abort = True
                self.logger.error("Camera exposure time smaller than readout time")
        else:
            self.logger.error("Camera handle empty")

    def set_exposure(self, exposure_ms):
        self.exposure_ms = exposure_ms
        self.setup()
        if self.gui_on:
            self.sig_update_gui.emit()

    def setup_triggers(self):
        if self.dev_handle:
            if self.trigger_in:
                dicti = {'NORMAL': 1, 'START': 6}
                self._set_property_from_dict('trig_in_mode', dicti)

                dicti = {'EXTERNAL': 1, 'SOFTWARE': 2}
                self._set_property_from_dict("master_pulse_source", dicti)

                dicti = {'INTERNAL': 1, 'EXTERNAL': 2, 'SOFTWARE': 3, 'MASTER_PULSE': 4}
                self._set_property_from_dict("trig_in_source", dicti)

                dicti = {'EDGE': 1, 'LEVEL': 2, 'SYNCREADOUT': 3}
                self._set_property_from_dict('trig_in_type', dicti)

                dicti = {'NEGATIVE': 1, 'POSITIVE': 2}
                self._set_property_from_dict('trig_in_polarity', dicti)

                if self.config['trig_in_source'] == 'MASTER_PULSE':
                    dicti = {'CONTINUOUS': 1, 'START': 2, 'BURST': 3}
                    self._set_property_from_dict('master_pulse_mode', dicti)
                    self.dev_handle.setPropertyValue("master_pulse_burst_times", self.config['master_pulse_burst_times'])
                    self.dev_handle.setPropertyValue("master_pulse_interval", self.config['master_pulse_interval_s'])
            else:  # reset trigger_in to default values
                self.dev_handle.setPropertyValue("trigger_mode", 1)  # NORMAL / 1
                self.dev_handle.setPropertyValue("master_pulse_trigger_source", 2)  # SOFTWARE
                self.dev_handle.setPropertyValue("trigger_source", 1)  # INTERNAL
                self.dev_handle.setPropertyValue("trigger_active", 1)  # EDGE / 1
                self.dev_handle.setPropertyValue("master_pulse_mode", 1)  # CONTINUOUS /1
                self.dev_handle.setPropertyValue("master_pulse_burst_times", 1)
                self.dev_handle.setPropertyValue("master_pulse_interval", 0.1)

            # Trigger OUT
            if self.trigger_out:
                dicti = {'LOW': 1, 'EXPOSURE': 2, 'PROGRAMMABLE': 3, 'TRIGGER READY': 4, 'HIGH': 5}
                self._set_property_from_dict('trig_out_kind', dicti)

                if self.config['trig_out_kind'] == 'PROGRAMMABLE':
                    dicti = {'READOUT_END': 2, 'VSYNC': 3, 'MASTER_PULSE': 6}
                    self._set_property_from_dict('trig_out_source', dicti)

                self.dev_handle.setPropertyValue("output_trigger_period[0]", self.config['trig_out_duration_s'])

                dicti = {'NEGATIVE': 1, 'POSITIVE': 2}
                self._set_property_from_dict('trig_out_polarity', dicti)
            else:  # defaults
                self.dev_handle.setPropertyValue("output_trigger_kind[0]", 2)
                self.dev_handle.setPropertyValue("output_trigger_source[0]", 2)
                self.dev_handle.setPropertyValue("output_trigger_period[0]", 0.001)
                self.dev_handle.setPropertyValue("output_trigger_polarity[0]", 2)
        else:
            self.logger.error('Camera handle is empty. Please initialize camera first.')

    def setup_trig_in(self, trig_in):
        self.trigger_in = trig_in
        self.setup_triggers()

    def setup_trig_out(self, trig_out):
        self.trigger_out = trig_out
        self.setup_triggers()

    def _set_property_from_dict(self, prop_name, prop_dict):
        """Search the dictionary keys for property name. If found, set corresponding
        camera property to dictionary value. Otherwise, throw an error."""
        if self.config[prop_name] in prop_dict.keys():
            # rename some properties to camera's native key words (sometimes oddly named)
            if prop_name == 'trig_in_mode':
                dev_prop_name = "trigger_mode"
            elif prop_name == 'trig_in_type':
                dev_prop_name = "trigger_active"
            elif prop_name == 'trig_in_source':
                dev_prop_name = 'trigger_source'
            elif prop_name == 'trig_in_polarity':
                dev_prop_name = 'trigger_polarity'
            elif prop_name == 'master_pulse_source':
                dev_prop_name = 'master_pulse_trigger_source'
            elif prop_name == 'trig_out_kind':
                dev_prop_name = 'output_trigger_kind[0]'
            elif prop_name == 'trig_out_source':
                dev_prop_name = "output_trigger_source[0]"
            elif prop_name == 'trig_out_polarity':
                dev_prop_name = "output_trigger_polarity[0]"
            else:
                dev_prop_name = prop_name
            self.dev_handle.setPropertyValue(dev_prop_name, prop_dict[self.config[prop_name]])
        else:
            self.logger.error(f"{prop_name} mode unknown: {self.config[prop_name]}")

    def snap(self):
        self.setup()
        if self.config['simulation']:
            self.last_image = np.random.randint(100, 200, size=self.config['image_shape'], dtype='uint16')
        elif self.dev_handle is not None:
            self.dev_handle.setACQMode("fixed_length", number_frames=1)
            self.dev_handle.startAcquisition()
            [frames, dims] = self.dev_handle.getFrames()
            self.dev_handle.stopAcquisition()
            if len(frames) > 0:
                self.last_image = np.reshape(frames[0].getData().astype(np.uint16), dims)
            else:
                self.logger.error("Camera buffer empty")
                self.last_image = np.zeros(self.config['image_shape'])
        else:
            self.logger.error("Camera is not initialized!")
            self.last_image = np.random.randint(100, 200, size=self.config['image_shape'], dtype='uint16')

    def disconnect(self):
        """Close the connection to camera"""
        if self.dev_handle is not None:
            self.dev_handle.shutdown()
            self.dev_handle = None
            self.logger.info("Camera disconnected")
            self.status = 'Not_connected'
        else:
            self.logger.error("Camera already disconnected")

    def set_frame_height(self, new_height):
        self.frame_height_px = int(new_height)
        self.set_readout_time(new_height)
        if self.gui_on:
            self.sig_update_gui.emit()
        if self.dev_handle is not None:
            self.cam_voffset = int((self.config['sensor_shape'][0] - self.frame_height_px) / 2.0)
            img_voffset = int((self.last_image.shape[0] - self.frame_height_px) / 2.0)
            self.dev_handle.setPropertyValue("subarray_vsize", self.frame_height_px)
            self.dev_handle.setPropertyValue("subarray_vpos", self.cam_voffset)
            if (img_voffset >= 0) and (img_voffset + self.frame_height_px < self.last_image.shape[0]):
                self.last_image = self.last_image[img_voffset:(img_voffset + self.frame_height_px), :]
            else:
                self.last_image = np.random.randint(100, 200,
                                              size=(self.frame_height_px, self.last_image.shape[1]), dtype='uint16')
            #self.display_image(self.last_image, position=(0, cam_voffset))
            self.logger.debug(f"New image dimensions {self.last_image.shape}")
            v_pos = self.dev_handle.getPropertyValue("subarray_vpos")[0]
            self.logger.debug(f"New subarray_vpos: {v_pos}")
        else:
            self.logger.error("Camera is not initialized!")

    def set_readout_time(self, vsize):
        """Compute the frame readout time based on its vertical extent.
        Assuming triggered Sync Readout mode.
        Parameters:
            vsize: int
                Number of rows in the frame (ROI).
        """
        h1 = 9.74436E-3  # 1-row readout time, ms
        self.frame_readout_ms = ((vsize / 2.0) + 5) * h1

    def update_config(self, key, value):
        if key in self.config.keys():
            self.config[key] = value
            self.logger.info(f"changed {key} to {value}")
        else:
            self.logger.error("Parameter name not found in config file")
        if self.gui_on:
            self.sig_update_gui.emit()

    def _setup_gui(self):
        self.gui.add_tabs("Control Tabs", tabs=['Control', 'Trigger IN', 'Trigger OUT'])
        tab_name = 'Control'
        self.gui.add_checkbox('Simulation', tab_name,
                              value=self.config['simulation'],
                              func=partial(self.update_config, 'simulation'))

        groupbox_name = 'Connection'
        self.gui.add_groupbox(title=groupbox_name, parent=tab_name)
        self.gui.add_button('Initialize', groupbox_name, lambda: self.initialize())
        self.gui.add_button('Disconnect', groupbox_name, lambda: self.disconnect())
        self.gui.add_string_field('Status', groupbox_name, value=self.status, enabled=False)

        groupbox_name = 'Frame control'
        self.gui.add_groupbox(title=groupbox_name, parent=tab_name)
        self.gui.add_numeric_field('Exposure, ms', groupbox_name,
                                   value=self.exposure_ms,
                                   vrange=[0, 1000, 1],
                                   func=self.set_exposure)
        self.gui.add_numeric_field('Image height, px', groupbox_name,
                                   value=self.frame_height_px,
                                   vrange=[128, self.config['sensor_shape'][0], 1],
                                   func=self.set_frame_height)
        self.gui.add_numeric_field('Readout time, ms', groupbox_name,
                                   value=self.frame_readout_ms,
                                   vrange=[0, 10, 0.1],
                                   enabled=False)

        tab_name = 'Trigger IN'
        self.gui.add_checkbox('Trigger in', tab_name, self.trigger_in, func=self.setup_trig_in)
        self.gui.add_string_field('trig_in_mode', tab_name, value=self.config['trig_in_mode'], enabled=False)
        self.gui.add_string_field('trig_in_source', tab_name, value=self.config['trig_in_source'], enabled=False)
        self.gui.add_string_field('trig_in_type', tab_name, value=self.config['trig_in_type'], enabled=False)
        self.gui.add_string_field('master_pulse_source', tab_name,
                                  value=self.config['master_pulse_source'], enabled=False)
        self.gui.add_string_field('master_pulse_mode', tab_name, value=self.config['master_pulse_mode'], enabled=False)
        self.gui.add_numeric_field('master_pulse_burst_times', tab_name,
                                   value=self.config['master_pulse_burst_times'], decimals=0, enabled=False)
        self.gui.add_numeric_field('master_pulse_interval_s', tab_name,
                                   value=self.config['master_pulse_interval_s'], decimals=3, enabled=False)

        tab_name = 'Trigger OUT'
        self.gui.add_checkbox('Trigger out', tab_name, self.trigger_out, func=self.setup_trig_out)
        self.gui.add_string_field('trig_out_kind', tab_name, value=self.config['trig_out_kind'], enabled=False)
        self.gui.add_string_field('trig_out_source', tab_name, value=self.config['trig_out_source'], enabled=False)
        self.gui.add_numeric_field('trig_out_duration_s', tab_name,
                                   value=self.config['trig_out_duration_s'],
                                   vrange=[0, 10, 0.001], enabled=False)
        self.gui.add_string_field('trig_out_polarity', tab_name,
                                  value=self.config['trig_out_polarity'], enabled=False)

    @QtCore.pyqtSlot()
    def _update_gui(self):
        self.gui.update_param('Status', self.status)
        self.gui.update_param('Readout time, ms', self.frame_readout_ms)


# run if the module is launched as a standalone program
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dev = CamController()
    dev.gui.show()
    app.exec_()

#
# The MIT License
#
# Copyright (c) 2013 Zhuang Lab, Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
