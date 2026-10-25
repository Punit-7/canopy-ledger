-- District and state names. No geometry columns: they are huge and we only need the labels.
SELECT gid_0, gid_1, name_1, gid_2, name_2, type_2, engtype_2, adm_level, gfw_area__ha
FROM data
WHERE gid_0 = '{iso}'
