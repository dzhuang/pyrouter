DEFAULT_PUBLIC_KEY = ("MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoVBwJv2pBtrr9Z"
                      "Y9C4lgqNo5+dFI+3A6W80h+8CzpCxsgl8Dic7JYmcTfOrtYtYJ6Vm"
                      "a3ZWx+NK1bJk8DFipOnDewVVJ6wmucnryF3OlfcIjLZsYjh4Sq2md"
                      "Zfg0lOThTvh8z4V2jO6fWh91iwOOeCokGoMw9V+QyQevtCr5pSQIDAQAB")


def encrypt(passwd: str) -> str:
    """
    The encrypt method used to encrypt password, hacked from the following js:
    
    .. code-block:: javascript

        function securityEncode(b) {
            a = 'RDpbLfCPsJZ7fiv'
            c = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'
        
            var e = "", f, g, h, k, l = 187, n = 187;
            g = a.length;
            h = b.length;
            k = c.length;
            f = g > h ? g : h;
        
            for (var p = 0; p < f; p++) {
                n = l = 187,
                    p >= g ? n = b.charCodeAt(p) : p >= h ? l = a.charCodeAt(p) : (l = a.charCodeAt(p),
                        n = b.charCodeAt(p)),
                    e += c.charAt((l ^ n) % k);
            }
            return e
        }

    :param passwd: password string
    :return: encrypted password
    """  # noqa

    b = passwd
    a = "RDpbLfCPsJZ7fiv"
    c = ("yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43"
         "odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9a"
         "Yb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70T"
         "OoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUy"
         "VeU3sfQ1xtXcPcf1aT303wAQhv66qzW")
    g = len(a)
    h = len(b)
    k = len(c)
    e = ''

    for p in range(max(g, h)):
        n = l = 187  # noqa
        if p >= g:
            l = ord(b[p])  # noqa
        elif p >= h:
            n = ord(a[p])
        else:
            n = ord(a[p])
            l = ord(b[p])  # noqa
        e += chr(ord(c[n ^ l]) % k)
    return e
