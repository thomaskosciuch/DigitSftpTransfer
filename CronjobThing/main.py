from requests import get

def handler(event, context):
    print('pinging')
    a = get(url='https://osiris.api.qwnext.com/v1/sync_nbin_accounts/', timeout=1)
    b = get(url='https://duat.api.qwnext.com/v1/sync_nbin_accounts/', timeout=1)
    c = get(url='https://anubis.api.qwnext.com/v1/sync_nbin_accounts/', timeout=1)
    print(a.text, b, c)

if __name__ == "__main__":
    handler(None, None)
