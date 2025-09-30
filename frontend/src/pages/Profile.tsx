import React from 'react';
import { useParams } from 'react-router-dom';
import { Layout } from '../components/layout/Layout';
import { UserProfile } from '../components/user/UserProfile';

export const Profile: React.FC = () => {
  const { username } = useParams<{ username: string }>();

  if (!username) {
    return <div>Usuario no encontrado</div>;
  }

  return (
    <Layout>
      <UserProfile username={username} />
    </Layout>
  );
};