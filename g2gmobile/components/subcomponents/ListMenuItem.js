import React from 'react';
import {
    StyleSheet,
    TouchableHighlight
} from 'react-native';
import {
    Body,
    ListItem,
    Text,
    Icon,
    Left
} from "native-base";
import styles from '../../styles';

class ListMenuItem extends React.Component {
    render() {
        const onPress = this.props.onPress || function () { };
        return (
            <TouchableHighlight>
                <ListItem style={{ flex: 1, height: 80, borderBottomWidth: StyleSheet.hairlineWidth, borderColor: styles.primaryColor, backgroundColor: styles.primaryCream }} icon onPress={onPress}>
                    <Left>
                        <Icon style={{ color: styles.primaryColor }} name={this.props.icon} />
                    </Left>
                    <Body style={{ borderBottomWidth: 0 }}>
                        <Text>{this.props.text}</Text>
                    </Body>
                </ListItem>
            </TouchableHighlight>
        );
    }
}

export default ListMenuItem;