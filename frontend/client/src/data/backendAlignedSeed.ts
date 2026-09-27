export const seedAmenities = [
  { id: 1, name: "Spa", category: "SPA", status: "FREE", capacity: 2, description: "Full-service spa with massage and therapy rooms" },
  { id: 2, name: "Sauna", category: "SAUNA", status: "FREE", capacity: 4, description: "Steam and dry sauna room" },
  { id: 3, name: "Yoga Studio", category: "YOGA", status: "FREE", capacity: 10, description: "Guided yoga and meditation sessions" },
  { id: 4, name: "Main Pool", category: "POOL", status: "FREE", capacity: 20, description: "Outdoor swimming pool" },
  { id: 5, name: "Fitness Gym", category: "GYM", status: "FREE", capacity: 15, description: "Gym with weights and cardio machines" }
];

export const seedAssets = [
  { asset_id: 1, asset_type: "HVAC_UNIT", room_or_location: "Spa", risk: 84 }
];

export const seedBookings = [
  { booking_id: 1, guest_name: "Aarav Mehta", email: "aarav@example.com", room_number: "101" },
  { booking_id: 2, guest_name: "Diya Kapoor", email: "diya@example.com", room_number: "102" }
];

export const seedUsers = [
  { id: "MGR001", name: "Ananya Rao", role: "MANAGER", email: "ananya.manager@smartresort360.com" },
  { id: "ENG001", name: "Ravi Shah", role: "ENGINEERING", email: "ravi.eng@smartresort360.com" },
  { id: "TRN001", name: "Meera Nair", role: "STAFF", email: "meera.transport@smartresort360.com" }
];

export const schedulingFactors = [
  { factor: "Stay length", weight: "+24 pts" },
  { factor: "Guest tier", weight: "+22 pts" },
  { factor: "Wait time", weight: "+20 pts" }
];
