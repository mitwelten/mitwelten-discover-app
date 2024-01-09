# def parse_contents(content, name, date):
#     return dict(content=content, name=name, date=date)
#
#
# @app.callback(
#     Output(ID_NEW_NOTE_STORE, 'data'),
#     Input('upload-image', 'contents'),
#     State('upload-image', 'filename'),
#     State('upload-image', 'last_modified'),
#     State(ID_NEW_NOTE_STORE, 'data')
# )
# def update_output(list_of_contents, list_of_names, list_of_dates, store):
#     if list_of_contents is not None:
#         content = [
#             parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         for c in content:
#             store.append(c)
#     return store
#
#
# @app.callback(
#     Output('output-image-upload', "children"),
#     Input(ID_NEW_NOTE_STORE, "data"),
#     prevent_initial_call=True
# )
# def show_new_notes_from_store(data):
#     all_note_titles = []
#     for note in data:
#         all_note_titles.append(html.Div(note["name"]))
#     return all_note_titles
