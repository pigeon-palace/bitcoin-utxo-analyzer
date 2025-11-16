class LitecoinScriptHandler:
    def get_address_from_script(script):
        if 'addresses' in script:
            address = script['addresses'][0]
        elif script['type'] == 'pubkey':
            address = script['asm'].split(" ")[0]
        elif script['type'] == 'nonstandard':
            address = "UNKNOWN"
        elif script['type'] == 'nulldata':
            address = "UNKNOWN"
        elif script['type'] == 'witness_mweb_hogaddr':
            address = "hogwarts"
        elif script['type'] == 'witness_mweb_pegin':
            address = "hogwarts"
        else:
            raise Exception("script['type'] unknown", script['type'])
        return address
