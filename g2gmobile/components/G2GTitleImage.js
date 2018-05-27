import React from 'react';
import { Image, View } from 'react-native';

class G2GTitleImage extends React.Component {
    render() {
        return (
            <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
                <Image
                    source={require('../assets/icons/g2g-white.png')}
                    style={{ height: 45, width: 144}}
                />
            </View>
        );
    }
}

export default G2GTitleImage;
