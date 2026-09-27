(() => {
    const modal = document.getElementById("addressModal");
    const mapElement = document.getElementById("checkoutAddressMap");
    const statusElement = document.getElementById("locationPickerStatus");
    const previewButton = document.getElementById("previewAddressOnMap");
    const locationButton = document.getElementById("useCurrentLocation");

    if (!modal || !mapElement || !statusElement || !previewButton || !locationButton) {
        return;
    }

    const addressFields = {
        house: document.getElementById("id_house_name"),
        area: document.getElementById("id_area"),
        city: document.getElementById("id_city"),
        state: document.getElementById("id_state"),
        pincode: document.getElementById("id_pincode")
    };

    const apiKey = mapElement.dataset.googleMapsKey;
    let map;
    let marker;
    let geocoder;
    let mapsReady;

    function setStatus(message, type = "") {
        statusElement.textContent = message;
        statusElement.classList.toggle("is-error", type === "error");
        statusElement.classList.toggle("is-success", type === "success");
    }

    function setButtonsDisabled(disabled) {
        previewButton.disabled = disabled;
        locationButton.disabled = disabled;
    }

    function loadGoogleMaps() {
        if (mapsReady) {
            return mapsReady;
        }

        mapsReady = new Promise((resolve, reject) => {
            if (!apiKey) {
                reject(new Error("Google Maps is not configured. Add GOOGLE_MAPS_API_KEY to the server environment."));
                return;
            }

            const callbackName = "checkoutGoogleMapsReady";
            window[callbackName] = () => {
                delete window[callbackName];
                resolve();
            };
            window.gm_authFailure = () => {
                setStatus("Google Maps rejected the API key. Check API activation, billing, and website referrer restrictions.", "error");
            };

            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&callback=${callbackName}&v=weekly&language=en&region=IN`;
            script.async = true;
            script.onerror = () => {
                delete window[callbackName];
                reject(new Error("Google Maps could not be loaded. Check your connection and API key."));
            };
            document.head.appendChild(script);
        }).catch(error => {
            mapsReady = null;
            throw error;
        });

        return mapsReady;
    }

    async function ensureMap() {
        await loadGoogleMaps();

        if (!map) {
            map = new google.maps.Map(mapElement, {
                center: { lat: 22.9734, lng: 78.6569 },
                zoom: 5,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true,
                clickableIcons: false
            });
            geocoder = new google.maps.Geocoder();
            marker = new google.maps.Marker({
                map,
                draggable: true,
                title: "Delivery location"
            });

            marker.addListener("dragend", () => {
                const position = marker.getPosition();
                if (position) {
                    setStatus(
                        `Pin moved to ${position.lat().toFixed(5)}, ${position.lng().toFixed(5)}. This is a preview only.`,
                        "success"
                    );
                }
            });
        }

        mapElement.classList.add("is-visible");
        window.setTimeout(() => google.maps.event.trigger(map, "resize"), 100);
        return { map, marker, geocoder };
    }

    async function showLocation(latitude, longitude, title) {
        const current = await ensureMap();
        const position = { lat: latitude, lng: longitude };
        current.marker.setMap(current.map);
        current.marker.setPosition(position);
        current.marker.setTitle(title);
        current.map.setCenter(position);
        current.map.setZoom(16);
    }

    function getAddressQuery() {
        return [
            addressFields.house?.value,
            addressFields.area?.value,
            addressFields.city?.value,
            addressFields.state?.value,
            addressFields.pincode?.value,
            "India"
        ].filter(value => value && value.trim()).join(", ");
    }

    function getAddressComponent(components, type) {
        const component = components.find(item => item.types.includes(type));
        return component ? component.long_name : "";
    }

    previewButton.addEventListener("click", async () => {
        const query = getAddressQuery();
        if (!query || query === "India") {
            setStatus("Enter at least an area, city, or pincode first.", "error");
            return;
        }

        setButtonsDisabled(true);
        setStatus("Finding this address on Google Maps…");

        try {
            const current = await ensureMap();
            current.geocoder.geocode({ address: query, componentRestrictions: { country: "IN" } }, async (results, status) => {
                try {
                    if (status !== "OK" || !results.length) {
                        const detail = status === "ZERO_RESULTS"
                            ? "We couldn’t find that address. Check the details or use GPS instead."
                            : `Google Maps couldn’t find the address (${status}). Check the details and try again.`;
                        setStatus(detail, "error");
                        return;
                    }

                    const result = results[0];
                    const location = result.geometry.location;
                    await showLocation(location.lat(), location.lng(), "Delivery address");
                    setStatus("Address found. Check that the pin matches your delivery location. You can drag the pin to adjust the preview.", "success");
                } catch (error) {
                    setStatus(error.message || "Could not display the address on the map.", "error");
                } finally {
                    setButtonsDisabled(false);
                }
            });
        } catch (error) {
            setStatus(error.message || "Could not load Google Maps. Please try again.", "error");
            setButtonsDisabled(false);
        }
    });

    locationButton.addEventListener("click", async () => {
        if (!navigator.geolocation) {
            setStatus("Location access is not supported by this browser. You can search the address instead.", "error");
            return;
        }

        setButtonsDisabled(true);
        setStatus("Waiting for your location permission…");

        navigator.geolocation.getCurrentPosition(async position => {
            try {
                const { latitude, longitude } = position.coords;
                await showLocation(latitude, longitude, "Your current location");

                const current = await ensureMap();
                current.geocoder.geocode({ location: { lat: latitude, lng: longitude } }, (results, status) => {
                    if (status !== "OK" || !results.length) {
                        setStatus("Your location is shown. We couldn’t find address details, so you can enter them manually.", "error");
                        setButtonsDisabled(false);
                        return;
                    }

                    const components = results[0].address_components;
                    const houseNumber = getAddressComponent(components, "street_number");
                    const route = getAddressComponent(components, "route");
                    const area = getAddressComponent(components, "sublocality_level_1")
                        || getAddressComponent(components, "neighborhood")
                        || getAddressComponent(components, "sublocality");
                    const city = getAddressComponent(components, "locality")
                        || getAddressComponent(components, "postal_town")
                        || getAddressComponent(components, "administrative_area_level_2");
                    const state = getAddressComponent(components, "administrative_area_level_1");
                    const pincode = getAddressComponent(components, "postal_code");

                    if (houseNumber || route) addressFields.house.value = [houseNumber, route].filter(Boolean).join(" ");
                    if (area) addressFields.area.value = area;
                    if (city) addressFields.city.value = city;
                    if (state) addressFields.state.value = state;
                    if (pincode) addressFields.pincode.value = pincode;

                    setStatus("Location found. Review the address details and map pin before saving.", "success");
                    setButtonsDisabled(false);
                });
            } catch (error) {
                setStatus(error.message || "Your location was found, but the map could not be displayed.", "error");
                setButtonsDisabled(false);
            }
        }, error => {
            const messages = {
                1: "Location permission was denied. Allow access in your browser or enter the address manually.",
                2: "Your location is unavailable right now. Try again or enter the address manually.",
                3: "Location request timed out. Try again or enter the address manually."
            };

            setStatus(messages[error.code] || "Could not get your location. Please enter the address manually.", "error");
            setButtonsDisabled(false);
        }, {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 60000
        });
    });

    modal.addEventListener("shown.bs.modal", () => {
        if (map) {
            window.setTimeout(() => google.maps.event.trigger(map, "resize"), 100);
        }
    });

    modal.addEventListener("hidden.bs.modal", () => {
        if (marker && map) {
            marker.setPosition(null);
        }

        mapElement.classList.remove("is-visible");
        setStatus(apiKey
            ? "Enter your delivery address, then choose “Show address on map”."
            : "Google Maps is not configured yet. Add GOOGLE_MAPS_API_KEY to the server environment.");
        setButtonsDisabled(false);
    });
})();
