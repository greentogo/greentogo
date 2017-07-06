import React from 'react';
import {observer} from 'mobx-react';

import { MapView } from 'expo';

@observer
class MapScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Participating Restaurants'
        }
    }

    constructor(props) {
        super(props)
        this.state = {
            restaurants: null,
            error: null,
        }
    }

    componentDidMount() {
        return fetch('https://g2g.dreisbach.us/api/v1/restaurants/', {
                      method: 'GET'}
                    )
        .then((response) => response.json())
        .then((json) => {
            this.setState({restaurants: json.data})
        })
    }

    render() {
        return (
            <MapView style={{flex: 1}}
                initialRegion={{
                    latitude: 35.9940,
                    longitude: -78.8986,
                    latitudeDelta: 0.05,
                    longitudeDelta: 0.05
                }}>
            {this.state.restaurants.map(restaurant => (
                <MapView.Marker
                    key={restaurant.name}
                    coordinate={{latitude: restaurant.latitude,longitude: restaurant.longitude}}
                    title={restaurant.name}
                    description={restaurant.address}
                />
            ))}
            </MapView>
        )
    }
}

export default MapScreen;
