import React from 'react';
import { StyleSheet, Platform, Image, ImageBackground, Animated, Text, View } from 'react-native';
import { inject, observer } from 'mobx-react';
import { MapView } from 'expo';
import openMap from 'react-native-open-maps';

class FadeInView extends React.Component {
    state = {
        fadeAnim: new Animated.Value(0),  // Initial value for opacity: 0
    }

    componentDidMount() {
        this.cycleAnimation();
    }

    cycleAnimation() {
        Animated.sequence([
            Animated.timing(this.state.fadeAnim, { // Animate over time
                toValue: 1,                 // Animate to opacity: 1 (opaque)
                duration: 500              // Make it take a while
            }),
            Animated.timing(this.state.fadeAnim, {  // The animated value to drive
                toValue: 0,
                duration: 500,
                delay: 500                // Make it last for a little
            })
        ]).start(() => {                // Starts the animation
            this.cycleAnimation();
        });
    }

    render() {
        let { fadeAnim } = this.state;
        return (
            <Animated.View                 // Special animatable View
                style={{
                    ...this.props.style,
                    opacity: fadeAnim,         // Bind opacity to animated value
                }}
            >
                {this.props.children}
            </Animated.View>
        );
    }
}


@inject('appStore')
@observer
class MapScreen extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            locations: this.props.appStore.resturants,
            // locations: [],
            authToken: this.props.appStore.authToken,
            currentLocation: false,
        }
    }

    static navigationOptions = {
        title: 'Participating Restaurants',
        headerTitleStyle: { width: 300 }
    };

    componentWillMount() {
        console.log(this.props.appStore.resturants);
        this._getCurrentLocation();
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

    render() {
        const styles = StyleSheet.create({
            calloutTitle: {
                flex: 1,
                textAlign: 'left',
                fontSize: 20,
                fontWeight: 'bold',
            },
            calloutText: {
                flex: 1,
                textAlign: 'left'
            },
            calloutDirections: {
                flex: 1,
                textAlign: 'left',
                fontWeight: 'bold'
            }
        });
        let markers = []
        this.state.locations.map((marker, i) => {
            markers.push(
                <MapView.Marker
                    coordinate={{
                        latitude: marker.latitude,
                        longitude: marker.longitude
                    }}
                    // title={marker.name}
                    // description={marker.address}
                    // key={marker.name}
                    key={i}
                    ref={comp => this['callout-' + i] = comp}
                    zIndex={0}
                    onPress={() => {
                        markers.map((mark, index) => {
                            this['callout-' + index].setNativeProps({ zIndex: 0 })
                        })
                        this['callout-' + i].setNativeProps({ zIndex: 9999 })
                    }}
                >
                    {Platform.OS === 'ios' && <ImageBackground
                        source={require('../assets/icons/Drop-Pin_Box.png')}
                        style={{ height: 75, width: 75, zIndex: 1 }}
                    >
                        <Text style={{ width: 0, height: 0 }}>{Math.random()}</Text>
                    </ImageBackground>}
                    <MapView.Callout
                        style={{ width: 300, zIndex: 9999 }}
                        onPress={() => this._goToLocation(marker.latitude, marker.longitude, marker.name)}
                    >
                        <Text numberOfLines={1} style={styles.calloutTitle}>{marker.name}</Text>
                        <Text numberOfLines={1} style={styles.calloutText}>{marker.address}</Text>
                        <Text numberOfLines={1} style={styles.calloutDirections}>Tap for directions!</Text>
                    </MapView.Callout>
                </MapView.Marker>
            )
        })
        return (
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
                        <FadeInView>
                            <ImageBackground
                                source={require('../assets/icons/you.png')}
                                style={{ height: 15, width: 15 }}
                            >
                            </ImageBackground>
                        </FadeInView>
                    </MapView.Marker>
                }
                {markers}
            </MapView>
        )
    }
}

export default MapScreen;
