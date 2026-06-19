import os
from django.conf import settings

import Ice

# Load up Murmur slice file into Ice
import sys
_stderr, sys.stderr = sys.stderr, open(os.devnull, 'w')
Ice.loadSlice(['-I' + Ice.getSliceDir(), os.path.join(settings.MUMBLE_ROOT, settings.SLICE_FILE)])
sys.stderr = _stderr
import MumbleServer

class MumbleMeta():
    _meta = None
    _ice = None

    @property
    def meta(self):
        if self._meta:
            return self._meta
        try:
            self._ice = Ice.initialize([
                "--Ice.ImplicitContext=Shared",
                "--Ice.Default.EncodingVersion=1.0",
                f"--Ice.Default.InvocationTimeout={30 * 1000}",
                f"--Ice.MessageSizeMax={settings.ICE_MESSAGESIZE}",
            ])
            proxy = self._ice.stringToProxy(settings.ICE_HOST)
            secret = settings.ICE_SECRET
            if secret:
                self._ice.getImplicitContext().put("secret", secret)
            self._meta = MumbleServer.MetaPrx.checkedCast(proxy)
        except Exception as e:
            print(e)
            pass
        return self._meta


Meta = MumbleMeta()
