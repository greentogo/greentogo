import React from 'react';
import { Image } from 'react-native';
import { inject, observer } from 'mobx-react';
import axios from '../apiClient';
import { MapView } from 'expo';

@inject('appStore')
@observer
class MapScreen extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            locations: [],
            authToken: this.props.appStore.authToken
        }
    }

    componentWillMount() {
      axios.get('restaurants/', {
          headers: {
              'Authorization': `Token ${this.state.authToken}`
          }
      })
      .then((json) => {
        this.setState({locations: json.data.data})
      })
      .catch((e) => console.log(e))
    }

    static route = {
        navigationBar: {
            title: 'Participating Restaurants'
        }
    }

    render() {
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
                  </MapView.Marker>
                ))}
            </MapView>
        )
    }
}

export default MapScreen;
