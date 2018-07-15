import React from 'react';
import { StyleSheet, Image, TouchableOpacity, Text } from 'react-native';
import { inject, observer } from 'mobx-react';
import axios from '../apiClient';
import { MapView } from 'expo';
import openMap from 'react-native-open-maps';


@inject('appStore')
@observer
class MapScreen extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            locations: [],
            authToken: this.props.appStore.authToken,
            currentLocation: null
        }
    }

    componentWillMount() {
      axios.get('restaurants/', {
          headers: {
              'Authorization': `Token ${this.state.authToken}`
          }
      })
      .then((json) => {
        navigator.geolocation.getCurrentPosition(((user)=>{
            console.log(user.coords);
            this.setState({locations: json.data.data, currentLocation: user.coords})
        }))
      })
      .catch((e) => console.log(e))
    }


    static route = {
        navigationBar: {
            title: `Participating Restaurants`,
            renderRight: (route, props) =>  <TouchableOpacity><Text style={{
                fontSize: 50,
                color: 'white',
                paddingTop: 5,
                paddingLeft: 5
            }} onPress={
                /* Finds Current Location Apparently */
                console.log("boop")
                // this.navigator.geolocation.getCurrentPosition(((x)=>{
                //     console.log(x)
                // }))
        } >X</Text></TouchableOpacity>
        }
    }

    _goToLocation(latitude, longitude) {
        console.log("Map Being Called");
        console.log(latitude)
        console.log(longitude)
        openMap({ latitude: latitude, longitude: longitude });
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
            }
        });
        return (
            <MapView
               style={{flex: 1}}
               initialRegion={{
                    latitude: 35.9940,
                    longitude: -78.8986,
                    latitudeDelta: 0.05,
                    longitudeDelta: 0.05
                }}>
                {this.state.locations.map(marker => (
                  <MapView.Marker
                    coordinate={{
                        latitude: marker.latitude,
                        longitude: marker.longitude
                    }}
                    title={marker.name}
                    description={marker.address}
                    key={marker.name}
                  >
                    <Image
                      source={require('../assets/icons/Drop-Pin_Box.png')}
                      style={{ height: 75, width: 75 }}
                    />
                    <MapView.Callout
                    style={{width: 300}}
                    onPress={() => this._goToLocation(marker.latitude, marker.longitude)}
                    >
                        <Text numberOfLines={1} style={styles.calloutTitle}>{marker.name}</Text>
                        <Text numberOfLines={1} style={styles.calloutText}>{marker.address}</Text>
                        <Text numberOfLines={1} style={styles.calloutText}>Tap for directions!</Text>
                    </MapView.Callout>
                  </MapView.Marker>
                ))}
            </MapView>
        )
    }
}

export default MapScreen;
