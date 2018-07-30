import React from 'react';
import {
    View,
    Image,
} from 'react-native';
import { inject, observer } from "mobx-react";
import styles from "../../styles";
import axios from '../../apiClient';
import {
    Text,
} from "native-base";

@inject("appStore")
@observer
class CommunityBoxes extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            ...this.props.appStore.user,
            textColor: styles.primaryColor,
            totalBoxesReturned: false,
            totalUserBoxesReturned: false,
            color: styles.primaryColor,
            background: styles.primaryCream
        }
    }

    componentWillMount() {
        let color = styles.primaryColor;
        let background = styles.primaryCream;
        if (this.props.color){
            color = this.props.color;
        }
        if (this.props.background){
            background = this.props.background;
        }
        let authToken = this.props.appStore.authToken;
        axios.get(`/stats/${this.props.appStore.user.username}/`, {
            headers: {
                'Authorization': `Token ${authToken}`
            }
        }).then((response) => {
            if (response.data && response.data.data) {
                let userBoxes = false;
                if (response.data.data.total_user_boxes_returned && response.data.data.total_user_boxes_returned > 0){
                    userBoxes = response.data.data.total_user_boxes_returned;
                }
                this.setState({ totalUserBoxesReturned: userBoxes, totalBoxesReturned: response.data.data.total_boxes_returned, color, background });
            }
        }).catch((error) => {
            if ((error.status && error.status === 401) || (error.response && error.response.status && error.response.status === 401)) {
                this.props.appStore.clearAuthToken();
            };
        })
    }

    render() {
        return (
            <View>
                {this.state.totalBoxesReturned &&
                    <View style={{ flex: 1, backgroundColor: this.state.background, justifyContent: 'center', paddingTop: 10, }}>
                        <Text style={{ textAlign: 'center', color: this.state.color, fontWeight: 'bold', fontSize: 26 }}>Our community</Text>
                        <Text style={{ textAlign: 'center', color: this.state.color, fontWeight: 'bold', fontSize: 26 }}>has saved</Text>
                        <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                            <Text style={{ color: this.state.color, fontWeight: 'bold', fontSize: 40, paddingRight: 10 }}>{this.state.totalBoxesReturned}</Text>
                            <Image
                                source={require('../../assets/icons/GTG-Box-App.png')}
                                style={{ height: 35, width: 35 }}
                            />
                            <Text style={{ color: this.state.color, fontWeight: 'bold', fontSize: 40, paddingLeft: 10 }}>s</Text>
                        </View>
                        <Text style={{ textAlign: 'center', color: this.state.color, fontWeight: 'bold', fontSize: 26 }}>from a landfill</Text>
                    </View>
                }
                {this.state.totalUserBoxesReturned &&
                    <View style={{ flex: 1, justifyContent: 'center', backgroundColor: this.state.background, paddingTop: 10 }}>
                        <Text style={{ textAlign: 'center', color: this.state.color, fontWeight: 'bold', fontSize: 26 }}>You've saved</Text>
                        <View style={{ flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
                            <Text style={{ color: this.state.color, fontWeight: 'bold', fontSize: 40, paddingRight: 10 }}>{this.state.totalUserBoxesReturned}</Text>
                            <Image
                                source={require('../../assets/icons/GTG-Box-App.png')}
                                style={{ height: 35, width: 35 }}
                            />
                            <Text style={{ color: this.state.color, fontWeight: 'bold', fontSize: 40, paddingLeft: 10 }}>s</Text>
                        </View>
                    </View>
                }
            </View>
        )
    }
}

export default CommunityBoxes;
