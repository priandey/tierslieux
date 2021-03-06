from rest_framework import serializers
from location.models import Location, Status


class StatusSerializer(serializers.ModelSerializer):
    location = serializers.HyperlinkedRelatedField(
            source='location.slug',
            view_name='locations-detail',
            lookup_url_kwarg='slug',
            read_only=True
    )

    class Meta:
        model = Status
        fields = ['url', 'activity', 'description', 'location', 'open_date', 'close_date', 'volunteer', 'is_opened']
        read_only_fields = ['close_date', 'volunteer']


class LocationSerializer(serializers.ModelSerializer):
    moderator = serializers.HyperlinkedRelatedField(source='moderator.pk', view_name='users-detail', read_only=True)
    statuses = StatusSerializer(many=True, required=False)
    url = serializers.HyperlinkedIdentityField(
            view_name='locations-detail',
            lookup_field='slug'
    )

    class Meta:
        model = Location
        fields = ['pk',
                  'url',
                  'name',
                  'catchphrase',
                  'description',
                  'moderator',
                  'slug',
                  'statuses',
                  'latitude',
                  'longitude',
                  'address']