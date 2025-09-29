import os
from django.conf import settings

import Ice

# Load up Murmur slice file into Ice
Ice.loadSlice('', ['-I' + Ice.getSliceDir(), os.path.join(settings.MUMBLE_ROOT, settings.SLICE_FILE)])
import MumbleServer

class MumbleMeta():
    _meta = None

    @property
    def meta(self):
        if self._meta:
            return self._meta
        try:
            props = Ice.createProperties()
            props.setProperty("Ice.ImplicitContext", "Shared")
            props.setProperty('Ice.Default.EncodingVersion', '1.0')
            props.setProperty('Ice.Default.InvocationTimeout', str(30 * 1000))
            props.setProperty('Ice.MessageSizeMax', str(settings.ICE_MESSAGESIZE))
            idata = Ice.InitializationData()
            idata.properties = props

            # Create Ice connection
            ice = Ice.initialize(idata)
            # Configure Ice properties
            proxy = ice.stringToProxy(settings.ICE_HOST)
            secret = settings.ICE_SECRET
            if secret != '':
                ice.getImplicitContext().put("secret", secret)
            self._meta = MumbleServer.MetaPrx.checkedCast(proxy)
        except Exception as e:
            pass
        return self._meta


Meta = MumbleMeta()
