import React from 'react';
import {observer} from "mobx-react";
import styles from "../styles";

import {
    Container,
    Header,
    Body,
    Title,
    Content,
    Form,
    Item,
    Input,
    Button,
    List,
    ListItem,
    Text,
    Icon,
    Left,
    Right
} from "native-base";

import { MapView } from 'expo';

import stylesheet from "../styles";

@observer
class MapScreen extends React.Component {
    static route = {
        navigationBar: {
            title: 'Participating Restaurants'
        }
    }

    render() {
        return (
            <MapView style={{flex: 1}}
                     initialRegion={{
                latitude: 35.9940,
                longitude: -78.8986,
                latitudeDelta: 0.05,
                longitudeDelta: 0.05
            }} />
        )
    }
}

export default MapScreen;
