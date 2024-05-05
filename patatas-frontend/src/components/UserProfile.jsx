import React from 'react';
import "./UserProfile.css"
function UserProfile({ user }) {
  return (
    <div className="profile-container">
      <div className="profile-header">
        <img src={user.imageUrl} alt="Profile" className="profile-image"/>
        <h2>{user.name}</h2>
        <p>Exploring the world, one destination at a time.</p>
      </div>
      <div className="interests-container">
        {user.interests.map(interest => (
          <div key={interest} className="interest-item">
            {interest}
          </div>
        ))}
      </div>
      <p className="profile-description">
        Our travel arrangement system considers your interests to offer you personalized and engaging travel experiences.
      </p>
    </div>
  );
}

export default UserProfile;
