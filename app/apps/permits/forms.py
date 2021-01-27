from django import forms


class SearchForm(forms.Form):
    search_url = forms.CharField(
        label="Decos Join zoek pad",
        required=False,
    )
    bag_id = forms.CharField(
        label="Decos Join zoek op BAG ID",
        required=False,
    )
