import React from 'react';
import { Image, View } from 'react-native';

class G2GTitleImage extends React.Component {
    render() {
        return (
            <View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
                <Image
                    source={require('../assets/icons/g2g-cream.png')}
                    style={{ height: 50, width: 160}}
                />
            </View>
        );
    }
}

export default G2GTitleImage;
