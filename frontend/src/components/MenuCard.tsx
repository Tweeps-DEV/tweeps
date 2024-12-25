import { motion } from 'framer-motion';

interface MenuItemProps {
  title: string;
  description: string;
  price: string;
  image: string;
}

export const MenuCard = ({ title, description, price, image }: MenuItemProps) => (
  <motion.div
    whileHover={{ scale: 1.05 }}
    className="bg-white rounded-lg overflow-hidden shadow-lg w-full"
  >
    <div className="relative h-40 sm:h-48 overflow-hidden">
      <img
        src={image}
        alt={title}
        className="w-full h-full object-cover"
      />
    </div>
    <div className="p-8">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-2xl font-semibold">{title}</h3>
        <span className="text-[#f2ae2a] font-bold">{price}</span>
      </div>
      <p className="text-sm sm:text-base text-gray-600">{description}</p>
    </div>
  </motion.div>
);
