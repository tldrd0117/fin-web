
import React from 'react';

import { Story, Meta } from '@storybook/react';

import LoginButton from './LoginButton';


export default {
    title: 'LoginButton',
    component: LoginButton,
    decorators: [(Story) => 
        <div>
            <style jsx>{`
            `}</style>
            <Story/>
        </div>
    ]
} as Meta;
  
const Template: Story<any> = (args) => <LoginButton {...args} />;

export const Primary = Template.bind({});
Primary.args = {
};
