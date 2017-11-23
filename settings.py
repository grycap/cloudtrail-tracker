
table_name = "EventoCloudTrail_V3"

"""eventName 's that we DONT want to store - Filter"""
filterEventNames = ["get", "describe", "list", "info", "decrypt"]
index = 'userIdentity_userName-eventTime-index'