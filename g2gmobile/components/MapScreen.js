import React from 'react';
import { Platform, ImageBackground, Text, View, Image, TouchableOpacity, ActivityIndicator } from 'react-native';
import { inject, observer } from 'mobx-react';
import { MapView } from 'expo';
import openMap from 'react-native-open-maps';
import Flashing from './subcomponents/Flashing';
import styles from '../styles';


@inject('appStore')
@observer
class MapScreen extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            mapType: "OUT",
            currentLocation: false,
        }
    }

    static navigationOptions = ({ navigation }) => {
        const { state } = navigation;
        let titleText = "Participating Restaurants";
        if (state.params && state.params.title){
            titleText = state.params.title;
        }
        return {
            title: `${titleText}`,
            headerTitleStyle: { width: 300 }
        }
    };

    componentDidMount() {
        this._getCurrentLocation();
        this.props.appStore.getResturantData();
        // this._interval = setInterval(() => {
        //     this._getCurrentLocation();
        // }, 5000);
    }

    componentWillUnmount() {
        // clearInterval(this._interval);
    }

    _getCurrentLocation() {
        navigator.geolocation.getCurrentPosition(((user) => {
            this.setState({ currentLocation: user.coords })
        }))
    }

    _goToLocation(latitude, longitude, title) {
        openMap({ latitude: latitude, longitude: longitude, query: title });
    }

    _switchService = (type, titleText) => () => {
        this.setState({ mapType: type })
        const { setParams } = this.props.navigation;
        setParams({ title: titleText })
    }

    render() {
        let markers = [];
        if (this.props.appStore.resturants) {
            this.props.appStore.resturants.map((marker, i) => {
                if (marker.address && marker.latitude && marker.longitude && marker.service === this.state.mapType) {
                    markers.push(
                        <MapView.Marker
                            coordinate={{
                                latitude: marker.latitude,
                                longitude: marker.longitude
                            }}
                            key={i}
                            ref={comp => this['callout-' + i] = comp}
                        >
                            {Platform.OS === 'ios' && <ImageBackground
                                source={require('../assets/icons/Drop-Pin_Box.png')}
                                style={{ height: 75, width: 75, zIndex: 1 }}
                            >
                            </ImageBackground>}
                            <MapView.Callout
                                style={{ width: 300, zIndex: 9999 }}
                                onPress={() => this._goToLocation(marker.latitude, marker.longitude, marker.name)}
                            >
                                <Text numberOfLines={1} style={styles.mapCalloutTitle}>{marker.name}</Text>
                                <Text numberOfLines={1} style={styles.mapCalloutText}>{marker.address}</Text>
                                <Text numberOfLines={1} style={styles.mapCalloutDirections}>Tap for directions!</Text>
                            </MapView.Callout>
                        </MapView.Marker>
                    )
                }
            })
            return (
                <View style={{ flex: 1 }}>
                    <MapView
                        style={{ flex: 1 }}
                        initialRegion={{
                            latitude: 35.9940,
                            longitude: -78.8986,
                            latitudeDelta: 0.05,
                            longitudeDelta: 0.05
                        }}>
                        {this.state.currentLocation &&
                            <MapView.Marker
                                coordinate={{
                                    latitude: this.state.currentLocation.latitude,
                                    longitude: this.state.currentLocation.longitude
                                }}
                                title={"You"}
                                key={"You"}
                            >
                                <Flashing>
                                    <ImageBackground
                                        source={require('../assets/icons/you.png')}
                                        style={{ height: 15, width: 15 }}
                                    >
                                    </ImageBackground>
                                </Flashing>
                            </MapView.Marker>
                        }
                        {markers}
                    </MapView>
                    <View style={styles.bottomFixed}>
                        <TouchableOpacity onPress={this._switchService("OUT", "Participating Restaurants")}>
                            <Text style={styles.subscriptionBanner}>Participating Restaurants</Text>
                        </TouchableOpacity>
                        <TouchableOpacity onPress={this._switchService("IN", "Return A Box")}>
                            <Text style={styles.subscriptionBanner}>Return Box</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            )
        } else {
            return (
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#0000ff" />
                </View>
            )
        }
    }
}

export default MapScreen;
