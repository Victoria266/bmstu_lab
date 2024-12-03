from rest_framework import serializers

from .models import *


class ResourcesSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, resource):
        if resource.image:
            return resource.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Resource
        fields = ("id", "name", "status", "density", "image")


class ResourceSerializer(ResourcesSerializer):
    class Meta(ResourcesSerializer.Meta):
        fields = "__all__"


class ReportsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Report
        fields = "__all__"


class ReportSerializer(ReportsSerializer):
    resources = serializers.SerializerMethodField()
            
    def get_resources(self, report):
        items = ResourceReport.objects.filter(report=report)

        if report.status == 3:
            return [ResourceItemSerializerWithCalc(item.resource, context={"plan_volume": item.plan_volume, "volume": item.volume}).data for item in items]

        return [ResourceItemSerializer(item.resource, context={"plan_volume": item.plan_volume}).data for item in items]


class ResourceItemSerializer(ResourceSerializer):
    plan_volume = serializers.SerializerMethodField()

    def get_plan_volume(self, _):
        return self.context.get("plan_volume")


class ResourceItemSerializerWithCalc(ResourceItemSerializer):
    volume = serializers.SerializerMethodField()

    def get_volume(self, _):
        return self.context.get("volume")


class ResourceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceReport
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
