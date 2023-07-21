# def get_pax_tod(deployment_id,bucket_width_m,  time_from=None, time_to = None):
#     url = construct_url(f"sensordata/pax/{deployment_id}/time_of_day", {"bucket_width_m":bucket_width_m, "from":time_from,"to":time_to})
#     res = cr.get(url)
#     if res.status_code == 200:
#         return res.json()
#
#     return None