import httpx

timeout = httpx.Timeout(60.0)


class MicroserviceName(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            base_url='',
            # headers='',
            verify=False,
            timeout=timeout,
            **kwargs,
        )