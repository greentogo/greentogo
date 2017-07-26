import React from 'react';
import { Image, View } from 'react-native';

class HomeScreenGreenToGoImage extends React.Component {
    render() {
        return (
            <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
                <Image
                    source={require('../assets/icons/g2g-white.png')}
                    style={{ height: 50, width: 160}}
                />
            </View>
        );
    }
}

export default HomeScreenGreenToGoImage;
