LABEL name="isc-car-connector-tenable" \
			vendor="tenable.io" \
			summary="tenable connector to Connect Asset/Risk (CAR)" \
			description="Tenable connector feeds CAR with assets informations and vulnerabilities."

CMD python3 app.py -tio-access-key=${CONFIGURATION_AUTH_TIO_ACCESS_KEY} -tio-secret-key=${CONFIGURATION_AUTH_TIO_SECRET_KEY} -car-service-url=${CAR_SERVICE_URL} -car-service-key=${CAR_SERVICE_KEY} -car-service-password=${CAR_SERVICE_PASSWORD} -car-service-url-for-token=${CAR_SERVICE_URL_FOR_AUTHTOKEN} -car-service-token=${CAR_SERVICE_AUTHTOKEN} -source=${CONNECTION_NAME}
